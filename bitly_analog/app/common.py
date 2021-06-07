# ----- Общий функционал

from app.models import Log

# ----- Глобальные переменные 
UNKNOWN_NAME = 'UNKNOWN FUNCTION NAME'                                                  # ошибка установления процесса при записи лога 
            
def logger(owner, process, exec_msg):
    ''' Создание записи в таблице логирования Log. 
        Аргументы:
        owner    (Owner) -- объект пользователя 
        process  (str)   -- имя вызывающего фрейма/функции/процесса
        exec_msg (str)   -- сообщение о выполненных действиях
    '''
    try: # запись лога в БД 
        Log.objects.create(
            owner = owner,                                                          
            process = process,                            
            execute = exec_msg,
        )
    except:
        Log.objects.create(
            owner = owner or None,                                                          
            process = process or None,                            
            execute = 'Не удалось создать лог пользователя <{}> для процесса {}'.format(owner, process),
        )
        
 
def is_subpart_exists(request, sub_domain):
    ''' Проверка на уникальность субдомена. Возвращает Boolean: True, если есть совпадения, иначе False. 
        Аргументы:
        request    (HttpRequest) -- объект HTTP-запроса
        sub_domain (str)         -- имя субдомена
    '''
    return Url.objects.filter(subpart=sub_domain).exists()


def get_owner(request):
    ''' Возвращает объект анонимного пользователя, установленного по ключу сессии из запроса. 
        Аргументы:
        request (HttpRequest) -- объект HTTP-запроса
    '''
    msg = ''                                                                            # сообщение в лог
    if not request.session.exists(request.session.session_key):                         # наличие ключа сессии
        request.session.create()                                                        # создание сессии для нового пользователя
    try:
        # извлеченние пользователя или создание нового
        result  = Owner.objects.get_or_create(session = Session.objects.get(session_key = request.session.session_key))
    except IntegrityError:
        owner = None
        msg = DB_ERROR
    else: 
        if result[1]:                                                                   # создан новый пользователь
            owner = result[0]
            msg = 'Создан новый пользователь с ключом сессии: ' + result[0].session.session_key,
    finally:
        if result[1] or msg:                                                            # создан новый пользователь
            logger(owner, get_fname(inspect.currentframe()), msg)                       # запись лога в БД  
    return result[0]    # объект Owner из кортежа (object, create)



def get_fname(frame):
    ''' Возвращает имя вызывающего фрейма/функции. 
        Аргументы:
        frame (frame) -- объект вызывающего фрейма  
    '''
    try:
        fname = inspect.getframeinfo(frame).function                                     # имя фрейма/функции
    except:
        fname = UNKNOWN_NAME 
        logger(None, 'get_fname', 'Не удалось определить имя процесса.')
    return fname                                                                        



def paginate(object_list=[], page_number=1, onpage=10):
    ''' Пагинация объектов заданной модели. Возвращает сраницу списка - объект класса Paginator. 
        Аргументы:
        request     (HttpRequest) -- объект HTTP-запроса
        object_list (iterable)    -- список объектов для разбиения на страницы
        page_number (int)         -- начальная страница пагинации списка правил пользователя
        onpage      (int)         -- количество строк списка правил в таблице  
    '''
    paginator = Paginator(object_list, onpage) 
    return paginator.get_page(page_number) 


  
def redirect_to(request, rule_id):
    ''' Перенаправление на ресурс по оригинальной ссылке.
        Аргументы:
        request (HttpRequest) -- объект HTTP-запроса
        rule_id (int)         -- id правила в БД        
    '''
    try:
        url = Url.objects.get(id = rule_id)                                             # объект правила, соответствующий короткой ссылке
    except Url.DoesNotExist:
        raise Http404('В модели Url нет объекта с номером ' + str(rule_id))
    else:
        return redirect(url.link)                                                       # пренаправление по ссылке правила



def ajax_check_subpart(request, sub_domain=None):
    ''' Оповещение пользователя об уникальности субдомена при вводе оригинальной ссылки или изменении значения субдомена sub_domain. 
        Возвращает JSON-объект {'subpart_unique': <Boolean: true/false>}, как результат проверки по БД,
        либо {'error': 'error'} при пустом параметре в запросе. 
        Аргументы:
        request    (HttpRequest) -- объект HTTP-запроса
        sub_domain (str)         -- значение поля субдомена
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


def caching(request, owner, process, obj, cache_key, related_field, page_number=1):
    ''' Кэширование выборки модели. Возвращает словарь контекста. '''
    page_number = request.GET.get('page') or page_number                                # установка номера страницы для текущего отображения

    # КЭШИРОВАНИЕ 
    # выборка всех правил пользователя с сортирвкой по дате удаления 
    if 'cache_key' in cache and not obj:                                                # если не производилась запись объекта url в БД
        url_query = cache.get('cache_key')                                              # ВЫБОРКА ИЗ КЭША
        is_db_query = False                                                             # флаг сообщения в контексте 
        logger(owner, process, 'Создан кэш объектов правил Url.')
    else:
        is_db_query = True
        url_query = Url.objects.filter(
            collection__in = Collection.objects.select_related(related_field).filter(
                owner=owner)).order_by('expire_date')

        results = [url.to_json() for url in url_query]
        cache.set('cache_key', results, timeout=CACHE_TTL)                              # ЗАПИСЬ В КЭШ 

        #print('TTL: ' + str(cache.ttl('url')))                                         # TTL=300 по умолчанию # вывод в консоль для отладки  
    
    return {
        'url_query': url_query,                                                         # список всех правил пользователя
        'is_db_query': is_db_query,                                                     # Boolean (выборка из БД->True / из кэша->False)
        'page_obj': paginate(url_query, page_number, owner.trows_on_page),              # разбивка на страницы      
    }
    # ----- end of caching
