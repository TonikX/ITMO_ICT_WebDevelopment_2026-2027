from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Car, Owner


class OwnerForm(UserCreationForm):
    class Meta:
        model = Owner
        fields = [
            "username",
            "first_name",
            "last_name",
            "birth_date",
            "passport_number",
            "home_address",
            "nationality",
        ]
        widgets = {
            "birth_date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})
        }


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["plate", "brand", "model", "color"]
