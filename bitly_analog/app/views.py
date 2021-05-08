"""
Definition of views.
"""

import json
from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from app.models import Session, Owner, Url 
from app.forms import Mainform


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    
    mainform = Mainform(request.POST or None)

    # контекст HTML-страницы
    context = {
        'mainform': mainform,
        'title': 'Сервис коротких ссылок', 'year': datetime.now().year,
    }

    if request.method == 'POST':
        # проверка формы
        if mainform.is_valid():         
            url = mainform.save(commit=False)                                           # инициализация объекта Url
            url.short = '{}/{}'.format(mainform.cleaned_data['domain'], url.subpart)    # формирование короткой ссылки                     
            url.save()                                                                  # сохранение формы и запись объекта в БД
            Owner(session=get_owner(request).session, url=url).save()                   # запись правила в БД-коллекцию пользователя

            context.update({
                'mainform': Mainform(), # пустая форма
                'newUrl': 'Правило сохранено. {}'.format(url),
            })
        else:
            context.update({
                'errors': mainform.errors, # ошибки формы
            })

    return render(request, 'app/index.html', context)


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
            'is_subpart_unique': is_subpart_unique(request, sub_domain),    # уникален ли заданный субдомен
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

    # создание сессии нового пользователя
    if not request.session.exists(request.session.session_key):
        request.session.create()
     
    return Owner.objects.get_or_create(session = Owner.objects.get(session = session_key=request.session.session_key))[0]

def is_subpart_unique(request, sub_domain):
    ''' Проверка на уникальность субдомена. Возвращает Boolean значение. '''
    return not Url.objects.filter(subpart=sub_domain, owner=get_owner(request)).exists()

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