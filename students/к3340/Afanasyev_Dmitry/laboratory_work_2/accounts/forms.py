from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='Имя', max_length=30)
    last_name = forms.CharField(label='Фамилия', max_length=30)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class OwnerRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        fields = RegistrationForm.Meta.fields + ('birth_date', 'passport_number', 'home_address', 'nationality')
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
