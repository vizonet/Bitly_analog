"""
Definition of views.
"""

import json
from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from app.models import Owner, Url 
from app.forms import Mainform

TITLE = 'Сервис коротких ссылок'

def home(request):
    """Renders the home page."""
    global TITLE
    assert isinstance(request, HttpRequest)

    mainform = Mainform()

    return render(
        request, 'app/index.html',
        {
            'mainform': mainform,
            'title': TITLE, 'year': datetime.now().year,
        }
    )


def check_subpart(request, sub_domain=None):
    ''' Проверка на уникальность извлеченного из запроса субдомена в БД. 
        Возвращает JSON-объект {'subpart_unique': <Boolean: true/false>}, как результат проверки по БД,
        либо {'error': 'error'} при пустом параметре в запросе.  
    '''
    assert isinstance(request, HttpRequest)
    
    result = {}
    # Извлечение и проверка параметра запроса
    sub_domain = request.GET.get('subpart') if 'subpart' in request.GET else None

    # параметр запроса не пустой -> установка результата проверки значения по БД 
    if sub_domain is not None:
        result = { 
            'subpart_unique': False if Url.objects.filter(subpart=sub_domain, owner_set=get_owner(request)).exist() else True, 
            'session_key': request.session['sessoin_key'], # для проверки в JS
        }
    # параметр запроса пустой -> сообщение об ошибке       
    elif sub_domain == '':
        result = {
            'error': 'Ошибка: не указано значение субдомена!'
        } 

    return HttpResponse(json.dumps(result))


# ----- Дополнительные функции

def get_owner(request):
    ''' Возвращает объект анонимного пользователя, установленного по ключу сессии из запроса. '''
    return Owner.objects.get_or_create(session_key = request.session.session_key)

    

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