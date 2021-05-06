/* Набор функций для манипулирования частями ссылок */

let full,   // поле полной ссылки
    domain,     // поле домена
    subpart;    // поле субдомена

function let_short() {
    /* Ajax GET-запрос с параметром полной ссылки. 
     * Возвращает JSON-обдъект строковых значений домена и субдомена {'domain': <domain>, 'subpart': <subpart>}. 
     * */

    // DOM-элемент ссылки со значением поля  
    let url = document.createElement('a');
    url.href = full.value;

    // Получение частей ссылки по ключам из стандартного набора элемента 'a' - ['href','protocol','host','hostname','port','pathname','search','hash']

    // извлечение домена
    // let re = /https?:\/\/(?:[-\w]+\.)?([-\w]+)\.\w+(?:\.\w+)?\/?.*/i
    let domain_str = url['hostname'].replace('www', '');
    domain.value = domain_str;

    // извлечение субдомена
    let re = /[^\/]+/ig                                                     
    let subpart_str = url['pathname'].match(re)[0];
    subpart.value = subpart_str;


    // GET-запрос для проверки уникальности субдомена в БД
    let path = 'check_subpart/' + subpart_str;
    fetch_get(path)
        .then(
            
        )

    // POST-запрос для записи объектов ссылки в БД 
    data = {
        'url': full.value,
        'domain': domain_str,
        'subpart': subpart_str,
    }

    fetch_post('url_ajax')
        .then(
            // отправка запроса на таблицу
        )
}

// Установка обработки по событию загрузки DOM-дерева
document.addEventListener("DOMContentLoaded", function () {
    // Cвязь с полями формы
    full = document.getElementById('id_full');
    domain = document.getElementById('id_domain');
    subpart = document.getElementById('id_subpart');

    // установка обработчика по событию ввода данных в поле полной ссылки
    full.addEventListener('input', let_short());
    
    // установка обработчика по событию ввода данных в поле субдомена
    subpart.addEventListener('input', let_short()); 
})