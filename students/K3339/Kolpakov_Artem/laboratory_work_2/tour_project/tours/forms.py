from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Reservation, Review


class RegistrationForm(UserCreationForm):
    pass


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["tour"]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["start_date", "end_date", "text", "rating"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "text": forms.Textarea(attrs={"rows": 4}),
        }
