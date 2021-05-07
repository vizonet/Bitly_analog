/* Набор функций для манипулирования частями ссылок */

const def_link = 'https://';

let link,       // поле полной ссылки
    domain,     // поле домена
    subpart,    // поле субдомена
    errors;     // блок сообщений об ошибках

// Установка обработки по событию загрузки DOM-дерева
document.addEventListener('DOMContentLoaded', function () {
    // Cвязь с полями формы
    link = document.getElementById('id_link');
    domain = document.getElementById('id_domain');
    subpart = document.getElementById('id_subpart');
    errors = document.getElementById('errors');

    // обработчик смены значения поле полной ссылки
    link.addEventListener('change', handler);

    // обработчик смены значения в поле субдомена
    subpart.addEventListener('change', handler);
})

let handler = function let_short() {
    /* Ajax GET-запрос с параметром полной ссылки. 
     * Возвращает JSON-обдъект строковых значений домена и субдомена {'domain': <domain>, 'subpart': <subpart>}. 
     * */

    // Получение частей ссылки по ключам из стандартного набора свойств tag-элемента 'a' - 
    // - ['href', 'protocol', 'host', 'hostname', 'port', 'pathname', 'search', 'hash']

    // DOM-элемент ссылки со значением поля  
    let url = document.createElement('a');
    url.href = (link.value) ? link.value : def_link;

    // извлечение домена
    // let re = /https?:\/\/(?:[-\w]+\.)?([-\w]+)\.\w+(?:\.\w+)?\/?.*/i
    let domain_str = url['hostname'].replace('www.', '');
    domain.value = domain_str;

    // извлечение субдомена
    let re = /[^\/]+/ig                                                     
    let subpart_arr = url['pathname'].match(re);
    subpart.value = (subpart_arr !== null) ? subpart_arr[0] : ''; // пустая строка при некорректной ссылки 
    subpart_str = subpart.value;

    // GET-запрос для проверки уникальности субдомена в БД
    if (link.value) {
        if (subpart_str && subpart_str !== '') {
            let path = '/app/check_subpart/' + subpart_str + '/';
            fetch_get(path)
                .then(result =>
                    alert('Ответ сервера: ' + result)
                )
        } else {
            errors.innerHTML = 'Не установлен параметр субдомена!';
        }
    }

    /*
    // POST-запрос для записи объектов ссылки в БД 
    data = {
        'url': link.value,
        'domain': domain_str,
        'subpart': subpart_str,
    }

    fetch_post('url_ajax')
        .then(
            // формирование таблицы
        )
        */
}

