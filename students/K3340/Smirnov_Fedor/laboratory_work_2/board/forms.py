from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Booking, Comment


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name']


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['seat']

    def clean_seat(self):
        seat = self.cleaned_data['seat']
        flight = self.instance.flight
        if seat < 1 or seat > flight.seats:
            raise forms.ValidationError(f'Выберите место от 1 до {flight.seats}')
        if flight.bookings.filter(seat=seat).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Это место уже занято')
        return seat


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['flight_date', 'rating', 'text']
        widgets = {'flight_date': forms.DateInput(attrs={'type': 'date'})}


class TicketForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['ticket', 'checked_in']
