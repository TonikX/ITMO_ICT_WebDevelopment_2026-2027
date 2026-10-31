from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import Car, User


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "birth_date",
            "passport_number",
            "home_address",
            "nationality",
            "password1",
            "password2",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["registration_number", "brand", "model_name", "color"]
