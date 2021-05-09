"""
Definition of views.
"""

import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator

from app.models import Session, Owner, Url, Collection 
from app.forms import Mainform


def home(request, page_default=1, onpage=3):
    ''' Главная страница серсвиса. '''
    assert isinstance(request, HttpRequest)

    days_expire = 1 # срок жизни правила (сутки)
    default_data = {'expire_date': datetime.now().date() + timedelta(days=days_expire)}  # данные для начальной формы 
    mainform = Mainform(request.POST or default_data)

    # контекст HTML-страницы
    context = {
        'rules': Collection.objects.filter(owner = get_owner(request)),     # выборка правил пользователя для таблицы
        'mainform': mainform,
        'title': 'Сервис коротких ссылок', 'year': datetime.now().year,
        'savemsg': '', 
        'errors': {},  # ошибки валидации формы и логики создания правил сокращения. Формат: 'errors': { key: [ error ] }
    }

    if request.method == 'POST':
        # проверка формы
        if mainform.is_valid():         
            url = mainform.save(commit=False)                                               # инициализация объекта Url

            # проверка субдомена, запись правила и формирование сообщений  
            if not is_subpart_exists(request, url.subpart):
                url.short = '{}/{}'.format(mainform.cleaned_data['domain'], url.subpart)    # формирование короткой ссылки                     
                url.save()                                                                  # сохранение формы и запись объекта в БД
                Collection.objects.create(owner=get_owner(request), url=url)                # создание нового правила в БД-коллекцию пользователя
                mainform = Mainform(default_data)
                context.update({
                    'savemsg': 'Правило сохранено. {}'.format(url),
                })                
            else:
                mainform = Mainform(request.POST)
                context['errors'].update({
                    'Субдомен': ['Найден дубликат! Измените текущее значение.' ],
                })    
                
            context.update({
                'mainform': mainform,  # начальный набор параметров либо POST-данные при ошибках
            })
        else:
            context['errors'].update(mainform.errors)   # ошибки формы
    # --- end of POST

    # пагинация
    owner=get_object_or_404(Owner, pk=get_owner(request).id) 
    # выборка всех правил пользователя с сортирвкой по дате удаления
    rules_list = Url.objects.filter(collection__in=Collection.objects.select_related('url').filter(owner=owner)).order_by('expire_date')
    page_number = request.GET.get('page') or page_default

    context.update({'page_obj':  paginate(rules_list, page_number, onpage)})
    return render(request, 'app/index.html', context)


def paginate(object_list, page_number=1, onpage=10):
    ''' Пагинация объектов заданной модели. Возвращает сраницу списка - объект класса Paginator. '''
    paginator = Paginator(object_list, onpage) 
    return paginator.get_page(page_number) 



def redirect_to(request, rule_id):
    ''' Перенаправление на ресурс по ссылке правила. '''
    try:
        url = Url.objects.get(id = rule_id)     # объект правила, соответствующий короткой ссылке
    except Url.DoesNotExist:
        raise Http404('В модели Url нет объекта с номером ' + str(rule_id))
    else:
        return redirect(url.link)               # пренаправление по ссылке правила



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
            'session_key': request.session.session_key,                     # для проверки в JS
            'is_subpart_exists': is_subpart_exists(request, sub_domain),    # существует ли заданный субдомен
        }
    # сообщение об ошибке
    else:
        result = {
            'error': 'Ошибка: ' + 'не указано значение субдомена!' if sub_domain == '' else 'отсутствует значение субдомена в запроосе!'
        } 
    return HttpResponse(json.dumps(result))



# ----- Дополнительные функции

def get_owner(request):
    ''' Возвращает объект анонимного пользователя, установленного по ключу сессии из запроса. '''
    if not request.session.exists(request.session.session_key): 
        request.session.create() # создание сессии нового пользователя  
    return Owner.objects.get_or_create(session = Session.objects.get(session_key = request.session.session_key))[0]   # Owner из кортежа (object, create)



def is_subpart_exists(request, sub_domain):
    ''' Проверка на уникальность субдомена. Возвращает Boolean: True, если есть совпадения, иначе False. '''
    return Url.objects.filter(subpart=sub_domain).exists()



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