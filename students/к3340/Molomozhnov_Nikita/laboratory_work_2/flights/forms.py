from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Reservation, Review


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'passport_number', 'home_address', 'nationality']


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = []


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['flight_date', 'text', 'rating']
        widgets = {
            'flight_date': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea(attrs={'rows': 3}),
        }