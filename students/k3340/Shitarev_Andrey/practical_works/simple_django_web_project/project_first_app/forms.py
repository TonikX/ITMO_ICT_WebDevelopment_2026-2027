from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Owner, Car


class OwnerForm(UserCreationForm):
    class Meta:
        model = Owner
        fields = ('username', 'first_name', 'last_name', 'birth_date', 'passport_number', 'home_address', 'nationality')


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ('registration_number', 'brand', 'model', 'color')
