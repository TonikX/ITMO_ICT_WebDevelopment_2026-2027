"""Формы приложения "Автовладельцы" (Практика 3).

Форма создания учётной записи с дополнительными атрибутами владельца:
номер паспорта, домашний адрес, национальность.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserRegisterForm(UserCreationForm):
    """Регистрация пользователя-владельца с новыми полями."""

    passport_number = forms.CharField(label='Номер паспорта', max_length=30)
    home_address = forms.CharField(label='Домашний адрес', max_length=200)
    nationality = forms.CharField(label='Национальность', max_length=50)

    class Meta:
        model = User
        # Пароль (password1/password2) добавляется формой автоматически.
        fields = ('username', 'passport_number', 'home_address', 'nationality')
        help_texts = {'username': 'Логин для входа.'}
