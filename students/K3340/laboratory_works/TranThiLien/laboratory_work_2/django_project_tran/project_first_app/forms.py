from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Car, CarOwner


class CarOwnerForm(UserCreationForm):
    """
    Практика 2.2 (форма владельца, FBV) + практика 2.3:
    создание пользователя с новыми атрибутами.
    """

    class Meta(UserCreationForm.Meta):
        model = CarOwner
        fields = ('username', 'last_name', 'first_name', 'birth_date',
                  'passport_number', 'home_address', 'nationality')
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}


class CarForm(forms.ModelForm):
    """Форма автомобиля для CreateView / UpdateView (практика 2.2)."""

    class Meta:
        model = Car
        fields = ['license_plate', 'brand', 'model', 'color']
