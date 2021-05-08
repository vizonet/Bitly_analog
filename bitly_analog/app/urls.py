''' Маршрутизация ссылок приложения. '''

from app import forms, views
from django.urls import path


urlpatterns = [
    path('ajax_check_subpart/<str:sub_domain>/', views.ajax_check_subpart, name='ajax_check_subpart'),  # проверка уникальности выбранного субдомена в БД
    path('redirect_to/<int:rule_id>/', views.redirect_to, name='redirect_to'),                        # перенаправление по ссылке
]

