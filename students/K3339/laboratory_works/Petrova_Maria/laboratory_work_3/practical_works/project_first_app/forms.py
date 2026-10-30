from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Car, CarOwner


class CarOwnerForm(UserCreationForm):
    class Meta:
        model = CarOwner
        fields = [
            "username", "last_name", "first_name", "email", "birth_date",
            "passport_number", "home_address", "nationality",
        ]
        labels = {
            "last_name": "Фамилия",
            "first_name": "Имя",
            "birth_date": "Дата рождения",
        }
        widgets = {
            "birth_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["license_plate", "brand", "model", "color"]
        labels = {
            "license_plate": "Госномер",
            "brand": "Марка",
            "model": "Модель",
            "color": "Цвет",
        }
