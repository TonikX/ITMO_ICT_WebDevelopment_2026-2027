from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CarOwnerCreationForm(UserCreationForm):
    passport_number = forms.CharField(label="Номер паспорта", max_length=20)
    home_address = forms.CharField(label="Домашний адрес", max_length=255)
    nationality = forms.CharField(label="Национальность", max_length=100)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "passport_number",
            "home_address",
            "nationality",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            "username": "Логин",
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Электронная почта",
            "password1": "Пароль",
            "password2": "Подтверждение пароля",
        }
        for field_name, label in labels.items():
            self.fields[field_name].label = label
