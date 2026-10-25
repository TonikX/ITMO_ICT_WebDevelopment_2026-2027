from django import forms
from .models import Booking, Review
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'full_name',
            'phone',
            'email',
            'people_count',
        ]

        labels = {
            'full_name': 'ФИО',
            'phone': 'Телефон',
            'email': 'Электронная почта',
            'people_count': 'Количество человек',
        }

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'password1',
            'password2',
        ]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            'text',
            'rating',
        ]