''' Маршрутизация ссылок приложения. '''

from app import forms, views
from django.urls import include, path

from rest_framework import routers
router = routers.DefaultRouter()                                                                        # на основе класса ModelViewSet
router.register(r'urls', views.UrlViewSet)

urlpatterns = [
    path('ajax_check_subpart/<str:sub_domain>/', views.ajax_check_subpart, name='ajax_check_subpart'),  # проверка уникальности выбранного субдомена в БД
    path('redirect_to/<int:rule_id>/', views.redirect_to, name='redirect_to'),                          # перенаправление по ссылке
    # api
    path('', include(router.urls)),
    #path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),                     # кнопка 'log in'
    path('urls_list/', views.UrlList.as_view()),                                                        # на основе класса ListAPIView
]

