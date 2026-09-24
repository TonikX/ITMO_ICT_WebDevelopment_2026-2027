from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CarOwner


class CarOwnerForm(forms.ModelForm):
    class Meta:
        model = CarOwner
        fields = [
            'username', 'last_name', 'first_name', 'birth_date',
            'passport_number', 'home_address', 'nationality',
        ]


class CarOwnerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CarOwner
        fields = UserCreationForm.Meta.fields + (
            'last_name', 'first_name', 'birth_date',
            'passport_number', 'home_address', 'nationality',
        )
