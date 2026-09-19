from django.contrib.auth.forms import UserCreationForm

from .models import CarOwner


class CarOwnerForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CarOwner
        fields = (
            "username",
            "first_name",
            "last_name",
            "birth_date",
            "passport_number",
            "home_address",
            "nationality",
        )
