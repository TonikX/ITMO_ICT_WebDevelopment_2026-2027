"""Формы регистрации, выступления и отзыва."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Registration, Review


class SignupForm(UserCreationForm):
    """Создаёт обычного пользователя без привилегий."""

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ["username", "first_name", "last_name", "email"]


class RegistrationForm(forms.ModelForm):
    """Поля, которыми автор управляет в своей регистрации."""

    class Meta:
        model = Registration
        fields = ["presentation_title", "abstract"]


class ReviewForm(forms.ModelForm):
    """Отзыв; автора и даты определяет сервер."""

    class Meta:
        model = Review
        fields = ["text", "rating"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4}),
            "rating": forms.NumberInput(attrs={"min": 1, "max": 10}),
        }


class ResultForm(forms.ModelForm):
    """Результат выступления для администратора."""

    class Meta:
        model = Registration
        fields = ["result"]
