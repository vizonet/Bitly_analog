/* Набор функций для манипулирования частями ссылок */

const def_link = 'https://',            // префикс ссылки 
    exists_key = 'is_subpart_exists';   // имя ключа Ajax-callback-ответа 


let link,           // поле полной ссылки
    domain,         // поле домена
    subpart,        // поле субдомена
    errors,         // блок сообщений об ошибках
    savemsg;        // блок сообщения о новом правиле в БД

// Инициализация после загрузки DOM-дерева
document.addEventListener('DOMContentLoaded', function () {
    // Cвязь с полями формы
    link = document.getElementById('id_link');
    domain = document.getElementById('id_domain');
    subpart = document.getElementById('id_subpart');

    // связь с блоками сообщений
    errors = document.getElementById('errors');
    savemsg = document.getElementById('savemsg');

    // обработчики 
    link.addEventListener('input', event => { // смена значения поле полной ссылки
        let_short(event);
    });
    subpart.addEventListener('input', event => { // смена значения в поле субдомена
        let_short(event);
    });
})

function let_short(event) {
    /* Ajax GET-запрос с параметром полной ссылки. 
     * Возвращает JSON-обдъект строковых значений домена и субдомена {'domain': <domain>, 'subpart': <subpart>}. 
     * */
    savemsg.innerHTML = ''; // очистка блока сообщений

    /* Получение частей ссылки по ключам из стандартного набора свойств tag-элемента 'a' -
       - ['href', 'protocol', 'host', 'hostname', 'port', 'pathname', 'search', 'hash']
    */
    // DOM-элемент ссылки со значением поля  
    let url = document.createElement('a');
    url.href = (link.value) ? link.value : def_link;

    // очистка блока ошибок
    if (link.value === '' || subpart === '') errors.innerHTML = ''; 

    // извлечение домена
    // let re = /https?:\/\/(?:[-\w]+\.)?([-\w]+)\.\w+(?:\.\w+)?\/?.*/i
    domain.value = url['hostname'].replace('www.', '');

    // извлечение субдомена при обновлении полной ссылки
    if (event.target != subpart) {
        let re = /[^\/]+/ig
        let subpart_arr = url['pathname'].match(re);
        subpart.value = (subpart_arr !== null) ? subpart_arr[0] : ''; // пустая строка при некорректной ссылке 
    }

    // GET-запрос для проверки уникальности субдомена в БД
    if (link.value) {
        if (subpart.value !== '') {
            let path = '/ajax_check_subpart/' + subpart.value + '/';
            fetch_get(path)
                .then(result => {
                    // вывод сообщений проверки субдомена
                    let msg = 'Субдомен "' + subpart.value + '" '; // начало сообщения
                    if (result.hasOwnProperty(exists_key)) { // проверка callback-ключа в ответе сервера
                        if (result[exists_key]) {
                            errors.innerHTML = msg + 'занят, измените текущее значение!';
                        } else {
                            errors.innerHTML = '<span style="color: green;">' + msg + 'свободен!</span>';
                        }
                    } else {
                        errors.innerHTML = 'Неожидаемый ответ сервера!';
                        // вывод всего словаря 'result' в консоль
                        console.log(errors.innerText);
                        for (key of Object.keys(result))
                            console.log(key + ': ' + result[key]);
                    }
                })
        } else {
            errors.innerHTML = 'Установите имя субдомена!';
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