
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User

class UserRegisterForm(UserCreationForm):

    passport_number = forms.CharField(label='Номер паспорта', max_length=30)
    home_address = forms.CharField(label='Домашний адрес', max_length=200)
    nationality = forms.CharField(label='Национальность', max_length=50)

    class Meta:
        model = User
        fields = ('username', 'passport_number', 'home_address', 'nationality')
        help_texts = {'username': 'Логин для входа.'}
