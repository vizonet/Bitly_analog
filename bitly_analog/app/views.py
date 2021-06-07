""" Definition of views. """

import json, time, threading, inspect

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, Http404
from django.db import IntegrityError 
from django.core.paginator import Paginator
from datetime import datetime, timedelta

from app.models import Log, Session, Owner, Url, Collection
from app.forms import Mainform

# cache
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings

# модули
from app.common import logger, is_subpart_exists, get_owner, get_fname, paginate, redirect_to, ajax_check_subpart, caching 
from app.periodic_tasks import clean_urls, scheduller
from app.api import UrlList, UrlViewSet

# ----- Глобальные переменные 
DB_ERROR = 'Ошибка доступа к БД.'                                                       # ошибка при обращении к БД для записи лога
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)                             # таймаут объектов кэша по умолчанию

# запуск задачи clean_rules после запуска проекта на host-сервере
scheduller(clean_urls, 'периодическая очистка URL-правил в БД')

# ----- Представления HTML-страниц 

def home(request):
    ''' Главная страница серсвиса. 
        Аргументы:
        request     (HttpRequest) -- объект HTTP-запроса
        page_number (int)         -- начальная страница пагинации списка правил пользователя
        onpage      (int)         -- количество строк списка правил в таблице  
    '''
    assert isinstance(request, HttpRequest)                                             # проверка принадлежности объекта запроса к своему классу
    url = None
    owner = get_owner(request)                                                          # инициализация пользователя
    process = get_fname(inspect.currentframe())                                         # имя текущей функции

    # данные для начальной формы - срок жизни правила (в сутках)
    default_data = {'expire_date': datetime.now().date() + timedelta(days=owner.url_ttl)} 
    savemsg = ''                                                                        # сообщение о записи правила в БД
    mainform = Mainform(request.POST or default_data)                                   # HTML-форма правила модели Url
    errors = {} # ошибки валидации формы и логики значений.                             # Формат: 'errors': { key: [ error ] }
    msg = ''                                                                            # сообщение в лог            
    # обработка и запись формы
    if request.method == 'POST':
        if mainform.is_valid():                                                         # учтена проверка субдомена          
            url = mainform.save(commit=False)                                           # инициализация объекта Url
            url.alias = '{}/{}'.format(mainform.cleaned_data['domain'], url.subpart)    # формирование короткой ссылки 
            url.owner = owner                                                           # добавление пользователя
            url.save()                                                                  # сохранение формы - запись объекта правила в БД
            logger(owner, process, 'Создан объект правила с id: ' + str(url.id))        # запись лога в БД 
            
            url_col = Collection.objects.create(owner=get_owner(request), url=url)      # создание нового правила в БД-коллекцию пользователя
            logger(owner, process, 
                   'Создан объект коллекци правил с id: ' + str(url_col.id))            # запись лога в БД  
            
            savemsg = '{}'.format(url)                                                  # из метода __str__ модели  
            mainform = Mainform(default_data)                                           # чистая форма после записи предыдущих данных
        else:
            errors = mainform.errors                                                    # ошибки валидации формы
    # --- end of POST

    # контекст HTML-страницы                                                             
    context = {
        'title': 'Сервис коротких ссылок', 'year': datetime.now().year,                 # заголовок страницы
        'mainform': mainform,
        'savemsg': savemsg,
        'errors': errors,
    }

    context.update(caching(request, owner, process, url, 'cache_key', 'url'))           # контекст кэширования
    return render(request, 'app/index.html', context)
