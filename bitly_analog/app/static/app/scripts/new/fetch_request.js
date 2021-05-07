/* Унифицированные GET/POST AJAX-запросы через JS-функцию fetch() */

// Формат URL: url='/<path>/'
// Использовать response.clone() для цепи промисов, т.к. response.json().locked=true после однократного преобразования

function fetch_get(url='') { 
	/* GET AJAX-запрос */
	return fetch(url)
		.then(
			response => {
				return response.json()
			}
		) 
		.catch(error => 
			alert("--> Ошибка при AJAX-запросе из 'fetch_get': " + error)
		)
}

function fetch_post(url='', data) {
	/* POST AJAX-запрос */ 
	const request = new Request(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; application/x-www-form-urlencoded; charset=UTF-8', // для формы // multipart - для файлов
			'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
			//'X-CSRFToken': getCookie('csrftoken') 	
		},
		credentials: 'include',
		body: JSON.stringify(data) // сериализация данных для тела запроса
	});
	return fetch(request) 
		.then(
			response => {
				return response.json()
			}
		)
		.catch(error =>
			alert("--> Ошибка при AJAX-запросе из 'fetch_post': " + error)
		)
}
