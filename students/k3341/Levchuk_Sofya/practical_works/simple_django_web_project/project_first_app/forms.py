from django import forms
from .models import CarOwner
from django.contrib.auth.forms import UserCreationForm


class OwnerForm(forms.ModelForm):
    class Meta:
        model = CarOwner
        fields = ['first_name', 'last_name', 'birth_date', 'passport', 'address', 'nationality']

class RegisterForm(UserCreationForm):
    class Meta:
        model = CarOwner
        fields = ['username', 'first_name', 'last_name', 'email',
                  'birth_date', 'passport', 'address', 'nationality']