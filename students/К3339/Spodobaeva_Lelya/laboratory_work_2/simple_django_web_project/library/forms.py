from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Reservation, Review


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["tourists_count", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text", "rating"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4}),
        }
