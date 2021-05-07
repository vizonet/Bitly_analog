''' Маршрутизация ссылок приложения. '''

from app import forms, views
from django.urls import path


urlpatterns = [
    # проверка уникальности выбранного субдомена в БД
    # path('check_subpart/', views.check_subpart, name='check_subpart'),  
    path('check_subpart/<str:sub_domain>/', views.check_subpart, name='check_subpart'),
]

