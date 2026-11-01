from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CarOwner

class OwnerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CarOwner
        # какие поля хотим видеть при регистрации
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'last_name', 'birth_date', 
            'passport_number', 'home_address', 'nationality'
        )
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }