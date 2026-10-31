from django import forms
from .models import CarOwner, Car

class CarOwnerForm(forms.ModelForm):
    class Meta:
        model = CarOwner
        fields = ['surname', 'name']

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['brand', 'model', 'color', 'gov_number']