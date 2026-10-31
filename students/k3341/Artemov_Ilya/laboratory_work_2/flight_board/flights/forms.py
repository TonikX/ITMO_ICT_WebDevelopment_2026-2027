from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Flight, Reservation, Review


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", max_length=150)
    last_name = forms.CharField(label="Фамилия", max_length=150)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ["username", "first_name", "last_name", "email"]


class FlightFilterForm(forms.Form):
    q = forms.CharField(label="Поиск", required=False, max_length=100,
                        widget=forms.TextInput(attrs={"placeholder": "Рейс, авиакомпания или аэропорт"}))
    direction = forms.ChoiceField(label="Тип рейса", required=False,
                                  choices=[("", "Все рейсы"), *Flight.Direction.choices])
    date = forms.DateField(label="Дата отлёта", required=False,
                          widget=forms.DateInput(attrs={"type": "date"}))


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["flight", "passenger_name", "seat_number"]
        help_texts = {"seat_number": "Нумерация начинается с 1. Занятые места указаны в списке пассажиров рейса."}


class CheckInForm(forms.ModelForm):
    ticket_number = forms.CharField(label="Номер билета", max_length=30)

    class Meta:
        model = Reservation
        fields = ["ticket_number"]


class StaffReservationForm(forms.ModelForm):
    ticket_number = forms.CharField(label="Номер билета", max_length=30)

    class Meta:
        model = Reservation
        fields = ["user", "passenger_name", "seat_number", "ticket_number"]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text", "rating"]
        widgets = {"text": forms.Textarea(attrs={"rows": 4}),
                   "rating": forms.NumberInput(attrs={"min": 1, "max": 10})}
