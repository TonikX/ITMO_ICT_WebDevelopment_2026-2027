from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Booking, Flight, Review, User


class SignupForm(UserCreationForm):
    first_name = forms.CharField(label='Имя', max_length=150)
    last_name = forms.CharField(label='Фамилия', max_length=150)
    email = forms.EmailField(label='Электронная почта')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class FlightFilterForm(forms.Form):
    origin = forms.CharField(label='Откуда', required=False, widget=forms.TextInput(attrs={'placeholder': 'Любой город'}))
    destination = forms.CharField(label='Куда', required=False, widget=forms.TextInput(attrs={'placeholder': 'Любой город'}))
    date = forms.DateField(label='Дата вылета', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    q = forms.CharField(label='Номер рейса или авиакомпания', required=False, widget=forms.TextInput(attrs={'placeholder': 'Например, NL 101'}))
    kind = forms.ChoiceField(label='Тип рейса', required=False, choices=[('', 'Все рейсы'), *Flight.Kind.choices])
    status = forms.ChoiceField(label='Статус', required=False, choices=[('', 'Любой статус'), *Flight.Status.choices])


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['passenger_name', 'seat']

    def __init__(self, *args, flight, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.flight = flight
        occupied = set(flight.bookings.exclude(pk=self.instance.pk).values_list('seat', flat=True))
        seats = [f'{n // 6 + 1}{"ABCDEF"[n % 6]}' for n in range(flight.capacity)]
        self.fields['seat'] = forms.ChoiceField(label='Место в салоне', choices=[(s, s) for s in seats if s not in occupied])


class StaffBookingForm(BookingForm):
    class Meta(BookingForm.Meta):
        fields = ['user', 'passenger_name', 'seat', 'ticket_number', 'checked_in']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {'rating': forms.Select(choices=[(i, f'{i} / 10') for i in range(10, 0, -1)]),
                   'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Что вам понравилось в полёте?'})}
