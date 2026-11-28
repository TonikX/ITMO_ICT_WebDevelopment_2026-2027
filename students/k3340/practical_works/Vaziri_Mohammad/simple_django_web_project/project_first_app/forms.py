from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Car, Owner


class OwnerCreationForm(UserCreationForm):
    """Практики 2.2 (форма ввода владельца) и 2.3 (создание пользователя с новыми атрибутами)."""

    class Meta(UserCreationForm.Meta):
        model = Owner
        fields = (
            "username",
            "last_name",
            "first_name",
            "birth_date",
            "passport_number",
            "home_address",
            "nationality",
        )
        widgets = {"birth_date": forms.DateInput(attrs={"type": "date"})}


class CarForm(forms.ModelForm):
    """Практика 2.2: форма для создания и обновления автомобилей (CBV)."""

    class Meta:
        model = Car
        fields = ("plate_number", "brand", "model", "color")
