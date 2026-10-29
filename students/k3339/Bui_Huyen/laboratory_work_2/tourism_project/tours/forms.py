from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Tour, Booking, Review

User = get_user_model()

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("people_count",)
        labels = {
            "people_count": "Количество человек",
        }
        widgets = {
            "people_count": forms.NumberInput(
                attrs={"min": 1, "value": 1}
            ),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("content", "score")
        labels = {
            "content": "Ваш отзыв",
            "score": "Оценка",
        }
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Поделитесь впечатлениями о туре...",
                }
            ),
            "score": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 10,
                }
            ),
        }