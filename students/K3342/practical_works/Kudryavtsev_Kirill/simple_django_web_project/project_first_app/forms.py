from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CarOwner


class OwnerForm(UserCreationForm):
    first_name = forms.CharField(label='Имя', max_length=150)
    last_name = forms.CharField(label='Фамилия', max_length=150)
    passport_number = forms.CharField(label='Номер паспорта', max_length=20)
    home_address = forms.CharField(label='Домашний адрес', max_length=200)
    nationality = forms.CharField(label='Национальность', max_length=80)

    class Meta(UserCreationForm.Meta):
        model = CarOwner
        fields = ['username', 'first_name', 'last_name', 'birth_date', 'passport_number', 'home_address', 'nationality']
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}
