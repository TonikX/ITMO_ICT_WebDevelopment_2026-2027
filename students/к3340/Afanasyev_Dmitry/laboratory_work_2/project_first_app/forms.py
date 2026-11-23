from django import forms
from .models import Car


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ('plate_number', 'brand', 'model_name', 'color')
