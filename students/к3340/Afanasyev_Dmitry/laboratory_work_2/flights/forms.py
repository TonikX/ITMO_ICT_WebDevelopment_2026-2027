from django import forms
from .models import Booking, Flight, Review


class FlightFilterForm(forms.Form):
    origin = forms.CharField(label='Откуда', required=False, max_length=100,
                             widget=forms.TextInput(attrs={'placeholder': 'Город вылета'}))
    destination = forms.CharField(label='Куда', required=False, max_length=100,
                                  widget=forms.TextInput(attrs={'placeholder': 'Город прилёта'}))
    q = forms.CharField(label='Поиск', required=False, max_length=100,
                        widget=forms.TextInput(attrs={'placeholder': 'Рейс, город или авиакомпания'}))
    direction = forms.ChoiceField(label='Тип рейса', required=False,
                                 choices=[('', 'Все рейсы')] + list(Flight.Direction.choices))
    date = forms.DateField(label='Дата вылета', required=False,
                          widget=forms.DateInput(attrs={'type': 'date'}))
    available = forms.BooleanField(label='Только свободные места', required=False)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('passenger_name', 'seat')

    def __init__(self, *args, flight, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.flight = flight
        occupied = set(flight.bookings.exclude(pk=self.instance.pk).values_list('seat', flat=True))
        choices = [(i, f'Место {i}') for i in range(1, flight.capacity + 1) if i not in occupied]
        self.fields['seat'] = forms.TypedChoiceField(label='Свободное место', choices=choices, coerce=int)


class CheckInForm(forms.ModelForm):
    ticket_number = forms.CharField(label='Номер билета', max_length=30)

    class Meta:
        model = Booking
        fields = ('ticket_number',)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'text')
        widgets = {'rating': forms.NumberInput(attrs={'min': 1, 'max': 10}),
                   'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Как прошёл ваш перелёт?'})}


class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ('number', 'airline', 'origin', 'destination', 'departure_at', 'arrival_at',
                  'direction', 'gate', 'capacity', 'status')
        widgets = {field: forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
                   for field in ('departure_at', 'arrival_at')}
