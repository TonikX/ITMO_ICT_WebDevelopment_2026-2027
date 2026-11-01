from django.contrib.auth.forms import UserCreationForm
from django.forms import DateInput, ModelForm

from .models import Car, CarOwner


class OwnerForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CarOwner
        fields = ["username", "first_name", "last_name", "birth_date", "passport_number", "home_address", "nationality"]
        widgets = {"birth_date": DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}


class CarForm(ModelForm):
    class Meta:
        model = Car
        fields = ["plate_number", "brand", "model_name", "color"]
