"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from app.models import Url

class Mainform(forms.ModelForm):
    ''' Форма ввода параметров для сокращения ссылки. '''
    class Meta:
        model = Url
        fields = '__all__'
        widgets = {
            'url': forms.URLInput(attrs={'class':'form-control'}),
            'domain': forms.TextInput(attrs={'class':'form-control', 'disable': 'disable'}),
            'subpart': forms.TextInput(attrs={'class':'form-control'}),
            'time_end': forms.DateInput(format=('%d.%m.%Y'), attrs={'class':'form-control'}),
        }

    domain = forms.CharField(label='Домен', widget=forms.TextInput)
    subpart = forms.CharField(label='Субдомен', widget=forms.TextInput)



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
