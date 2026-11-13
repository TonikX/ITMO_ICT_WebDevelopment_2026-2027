from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import User

class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_date',
                  'passport_number', 'address', 'nationality')
        widgets = {'birth_date': forms.DateInput(attrs={'type':'date'})}

class AccountChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'
