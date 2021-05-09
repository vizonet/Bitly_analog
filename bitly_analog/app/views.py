"""
Definition of views.
"""
import json
import time
import threading
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator

from app.models import Session, Owner, Url, Collection 
from app.forms import Mainform, is_subpart_exists

# ----- Периодические задачи

def clean_rules():                                                                      
    ''' Очистка в БД записей правил модели 'Url' с наступившей датой удаления 'expire_date'. 
        Вызывается асинхронно в отдельном потоке.
    '''
    while True:
        delay = 24*60*60  # одни сутки                                                  # время в секундах между вызовами функции
        # очистка правил в БД 
        Url.objects.filter(expire_date=datetime.now().date()).delete() 
        # очистка правил в кеше
        time.sleep(delay)                                                               # задержка
     

def scheduller(task): 
    ''' Запуск асинхронных задач. '''
    thread = threading.Thread(target=task)                                              # инициализация потока
    thread.start()
    print('Запущен асинхронный поток зачачи ' + task.__name__ + '\n')                   # запуск потока (сообщение в консоль сервера)

# scheduller(clean_rules)                                                                 # запуск задачи clean_rules

# ----- Представления HTML-страниц 

def home(request, page_number=1, onpage=3):
    ''' Главная страница серсвиса. 
        # Аргументы:
        # page_number       - начальная страница пагинации списка правил пользователя
        # onpage            - количество строк списка правил в таблице  
    '''
    assert isinstance(request, HttpRequest)                                             # проверка принадлежности объекта запроса к своему классу 
    owner=get_owner(request)                                                            # инициализация пользователя
    # данные для начальной формы - срок жизни правила (в сутках)
    default_data = {'expire_date': datetime.now().date() + timedelta(days=owner.url_ttl)} 
    savemsg = ''                                                                        # сообщение о записи правила в БД
    mainform = Mainform(request.POST or default_data)                                   # HTML-форма правила модели Url
    errors = {} # ошибки валидации формы и логики значений.                             # Формат: 'errors': { key: [ error ] }

    # обработка и запись формы
    if request.method == 'POST':
        if mainform.is_valid():                                                         # учтена проверка субдомена          
            url = mainform.save(commit=False)                                           # инициализация объекта Url
            url.alias = '{}/{}'.format(mainform.cleaned_data['domain'], url.subpart)    # формирование короткой ссылки 
            url.owner = owner                                                           # добавление пользователя
            url.save()                                                                  # сохранение формы - запись объекта правила в БД
            Collection.objects.create(owner=get_owner(request), url=url)                # создание нового правила в БД-коллекцию пользователя
            savemsg = '{}'.format(url)                                                  # из метода __str__ модели  
            mainform = Mainform(default_data)                                           # чистая форма после записи предыдущих данных
        else:
            errors = mainform.errors                                                    # ошибки валидации формы
    # --- end of POST

    # Пагинация
    # выборка всех правил пользователя с сортирвкой по дате удаления
    rules_query = Url.objects.filter(collection__in=Collection.objects.select_related('url').filter(owner=owner)).order_by('expire_date')
    # установка номера страницы для текущего отображения
    page_number = request.GET.get('page') or page_number

    # контекст HTML-страницы
    context = {
        'title': 'Сервис коротких ссылок', 'year': datetime.now().year,                 # загололвок HTML-страницы 
        'mainform': mainform,
        'savemsg': savemsg,
        'errors': errors,
        'rules_query': rules_query,                                                     # список всех правил пользователя
        'page_obj': paginate(rules_query, page_number, owner.trows_on_page),            # разбивка на страницы
    }
    return render(request, 'app/index.html', context)



def paginate(object_list=[], page_number=1, onpage=10):
    ''' Пагинация объектов заданной модели. Возвращает сраницу списка - объект класса Paginator. 
        # Аргументы:
        # object_list       - список объектов для разбиения на страницы
        # page_number       - начальная страница пагинации списка правил пользователя
        # onpage            - количество строк списка правил в таблице  
    '''
    paginator = Paginator(object_list, onpage) 
    return paginator.get_page(page_number) 


  
def redirect_to(request, rule_id):
    ''' Перенаправление на ресурс по ссылке правила. '''
    try:
        url = Url.objects.get(id = rule_id)                                             # объект правила, соответствующий короткой ссылке
    except Url.DoesNotExist:
        raise Http404('В модели Url нет объекта с номером ' + str(rule_id))
    else:
        return redirect(url.link)                                                       # пренаправление по ссылке правила



def ajax_check_subpart(request, sub_domain=None):
    ''' Оповещение пользователя об уникальности субдомена при вводе оригинальной ссылки или изменении значения субдомена. 
        Возвращает JSON-объект {'subpart_unique': <Boolean: true/false>}, как результат проверки по БД,
        либо {'error': 'error'} при пустом параметре в запросе.  
    '''
    assert isinstance(request, HttpRequest)
    result = {} # словарь callback-ответа 

    # параметр запроса не пустой -> установка результата проверки значения по БД 
    if sub_domain: 
        result = { 
            'is_subpart_exists': is_subpart_exists(request, sub_domain),                # существует ли заданный субдомен
        }
    # сообщение об ошибке
    else:
        result = {
            'error': 'Ошибка: ' + 'не указано значение субдомена!' if sub_domain == '' else 'отсутствует значение субдомена в запроосе!'
        } 
    return HttpResponse(json.dumps(result))



# ----- Дополнительный функционал

def get_owner(request):
    ''' Возвращает объект анонимного пользователя, установленного по ключу сессии из запроса. '''
    if not request.session.exists(request.session.session_key): 
        request.session.create() # создание сессии нового пользователя  
    return Owner.objects.get_or_create(session = Session.objects.get(session_key = request.session.session_key))[0]   # Owner из кортежа (object, create)


'''
def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )
'''