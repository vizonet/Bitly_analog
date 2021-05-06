''' Маршрутизация ссылок приложения. '''

from app import forms, views


urlpatterns = [
    path('check_subpart/<str:sub_domain>', views.check_subpart, name='check_subpart'),  # Проверка уникальности выбранного субдомена в БД
]

