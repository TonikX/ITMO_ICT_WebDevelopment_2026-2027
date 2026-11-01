from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Owner, Car


class OwnerForm(UserCreationForm):
    class Meta:
        model = Owner
        fields = ['username', 'first_name', 'last_name', 'birth_date', 'passport', 'address', 'nationality']
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['plate', 'brand', 'model', 'color']
