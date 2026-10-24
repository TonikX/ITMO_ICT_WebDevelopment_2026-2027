from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import Car, CarOwner


class CarOwnerCreateForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    first_name = forms.CharField(label='Имя', max_length=30)
    last_name = forms.CharField(label='Фамилия', max_length=30)
    passport_number = forms.CharField(label='Номер паспорта', max_length=20)
    address = forms.CharField(label='Домашний адрес', max_length=200)
    nationality = forms.CharField(label='Национальность', max_length=50)

    class Meta:
        model = CarOwner
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'birth_date',
            'passport_number',
            'address',
            'nationality',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password

    def save(self, commit=True):
        owner = super().save(commit=False)
        owner.set_password(self.cleaned_data['password'])
        if commit:
            owner.save()
        return owner


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['license_plate', 'brand', 'model_name', 'color']
