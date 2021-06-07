# ----------- API

# rest api
from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import UrlSerializer
from app.models import Url


class UrlList(generics.ListAPIView):
    ''' Возвращает все правила из БД. ''' 
    queryset = Url.objects.all().order_by('expire_date')
    serializer_class = UrlSerializer


class UrlViewSet(viewsets.ModelViewSet):
    ''' Возвращает все правила из БД. ''' 
    queryset = Url.objects.all().order_by('expire_date')
    serializer_class = UrlSerializer
