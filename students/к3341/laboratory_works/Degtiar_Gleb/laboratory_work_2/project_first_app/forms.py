from django import forms
from .models import Car
class CarForm(forms.ModelForm):
    class Meta:
        model=Car
        fields=['plate','brand','model_name','color']
