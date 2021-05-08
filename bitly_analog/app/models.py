"""
Definition of models.
"""

from django.db import models
from django.contrib.sessions.models import Session

# Create your models here.

class Url(models.Model):
    ''' Модель БД для хранения параметров правила сокращения ссылки. '''
    
    link = models.URLField('Оригинальная ссылка')
    short = models.CharField('Короткая cсылка', max_length=100)
    subpart = models.CharField('Субдомен', max_length=40)
    expire_date = models.DateField('Дата удаления правила')     
    # time_start = models.DateTimeField('Дата и время начала действия правила')     
    # ttl = models.DurationField('Период действия правила')
    str_limit = models.PositiveSmallIntegerField('Число первых символов отображения оригинального URL в методе __str__', default=40)


    def __str__(self):
        ''' Строковое представление модели. ''' 
        return 'Короткий URL: ' + self.short + ', оригинал: ' + self.link[:self.str_limit] + ('...' if len(self.link) > self.str_limit else '')

    def to_json(self):
        ''' Сведения об объекте модели. '''
        return {
            'id': self.id,
            'link': self.full,
            'short': self.short,
            'ttl': self.ttl,
        }


class Owner(models.Model):
    ''' Модель БД для хранения связей пользователей и их правил сокращения ссылок. '''
    session = models.ForeignKey(Session, on_delete=models.CASCADE)      # связь с таблицой Session
    url = models.ForeignKey(Url, on_delete=models.PROTECT, null=True)   # связь с таблицей правил Url 

    def __str__(self):
        ''' Строковое представление модели. ''' 
        return 'Owner key: {}'.format(self.session.session_key)


