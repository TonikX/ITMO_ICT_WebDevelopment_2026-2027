from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Car, CarOwner


class OwnerForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CarOwner
        fields = ['username', 'last_name', 'first_name', 'birth_date', 'passport', 'address', 'nationality']
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['plate', 'brand', 'model_name', 'color']
