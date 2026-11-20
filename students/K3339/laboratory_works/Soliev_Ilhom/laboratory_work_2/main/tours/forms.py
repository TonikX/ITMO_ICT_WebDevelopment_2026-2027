from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Booking, Review


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Почта")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["travelers", "phone", "comment"]
        widgets = {"comment": forms.Textarea(attrs={"rows": 3}),
                   "phone": forms.TextInput(attrs={"type": "tel"})}

    def clean(self):
        data = super().clean()
        if self.instance.tour.start_date < timezone.localdate():
            raise forms.ValidationError("Этот тур уже начался. Выберите другой тур.")
        return data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 4})}
