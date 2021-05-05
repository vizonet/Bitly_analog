"""
Definition of models.
"""

from django.db import models

# Create your models here.

class Link(models.Model):
    ''' Модель данных для хранения '''
    long = models.URLField('Оригинальная ссылка')
    short = models.CharField('Оригинальная ссылка')
    

    def __str__(self):
        return self.short 