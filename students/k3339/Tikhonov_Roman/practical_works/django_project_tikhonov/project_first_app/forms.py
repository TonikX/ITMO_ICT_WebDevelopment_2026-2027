from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Car, User


class UserForm(UserCreationForm):
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
        ]


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["state_number", "brand", "model", "color"]
