# ----- Периодические задачи

import threading, inspect
from app.common import logger, get_fname

def clean_urls(*args):                                                                      
    ''' Очистка в БД записей правил модели 'Url' с наступившей датой удаления 'expire_date'. 
        Вызывается асинхронно в отдельном потоке.
    '''
    msg = 'Периодическая задача: очистка в БД Url-объектов правил по текущую дату включительно. '
    while True:
        delay = 24*60*60  # одни сутки                                                  # время в секундах между вызовами функции
        # очистка правил в БД и логирование
        try: 
            query = Url.objects.filter(expire_date__lte=datetime.now().date())          # выборка всех правил до текущей даты включительно
        except NameError:
            msg += DB_ERROR + 'Таблица Url не найдена.' 
        else: 
            ids = [url.id for url in query]
            # сообщение в лог
            msg = ('Удалены правила ({}) с id : ' + str(len(ids)) + str(ids)) if query \
                else 'Нет правил для удаления.' + msg
            query.delete()                                                              # удаление правил с соответствующей датой
        finally:
            logger(None, get_fname(inspect.currentframe()), msg)                        # запись лога в БД  
        # очистка правил в кэше
        time.sleep(delay)                                                               # останов задачи на период


def scheduller(task, *args):
    ''' Выполняет запуск асинхронной задачи в потоке.
        Аргументы:
        task (str)      -- имя задачи/функции
        args (tuple)    -- аргументы задачи task
    '''
    thread = threading.Thread(target=task, args=args)                                  # инициализация потока
    try:
        thread.start()
    except:
        msg = 'Не удалось запустить асинхроную задачу.' + task.__name__ 
    else: 
        msg = '--> В асинхронном потоке запущена задача ' + task.__name__ \
                + ((': ' + args[0]) if args else '') + '\n'                            # сообщение в лог из аргументов 
    logger(None, get_fname(inspect.currentframe()), msg)                               # запись лога в БД  
    print(msg)                                                                         # сообщение в консоль сервера
