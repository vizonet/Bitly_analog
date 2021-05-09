"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from app.models import Url

class Mainform(forms.ModelForm):
    ''' Форма ввода параметров для сокращения ссылки. '''
    class Meta:
        model = Url
        fields = '__all__'
        exclude = ['short', 'str_limit']
        widgets = {
            'link': forms.URLInput(attrs={'class': 'form-control' }),
            'expire_date': forms.DateInput(format=('%d.%m.%Y'), attrs={'class': 'form-control', 'placeholder': 'дд.мм.гггг'}),
            'subpart': forms.TextInput(attrs={'class': 'form-control'}),
        }
    # дополнительное поле для формирования поля 'short' 
    domain = forms.CharField(label='Домен', widget=forms.TextInput(attrs={'class':' form-control', 'readonly': 'True'}))

    def clean(self):
        ''' Проверка значения поля 'subpart' на дубликат в БД. 
            При наличии дубликата инициирует добавленную в стандартный набор form.errors ошибку. 
        '''
        subpart = self.cleaned_data['subpart']  # значение поля 
        if Url.objects.filter(subpart=subpart).exists():  
            self.add_error('subpart', 'В БД найден дубликат субдомена! Измените текущее значение.')

'''
class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))
'''