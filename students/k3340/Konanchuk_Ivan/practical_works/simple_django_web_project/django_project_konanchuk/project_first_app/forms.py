from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CarOwner


class OwnerForm(UserCreationForm):
    class Meta:
        model = CarOwner
        fields = ["username", "last_name", "first_name", "birth_date",
                  "passport_number", "home_address", "nationality"]
        widgets = {"birth_date": forms.DateInput(attrs={"type": "date"})}
