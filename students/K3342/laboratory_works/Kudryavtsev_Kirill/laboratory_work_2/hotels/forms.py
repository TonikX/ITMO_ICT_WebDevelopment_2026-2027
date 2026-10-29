from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Booking, Review, Room


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='Имя', max_length=150)
    last_name = forms.CharField(label='Фамилия', max_length=150)
    email = forms.EmailField(label='Электронная почта')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class SearchForm(forms.Form):
    q = forms.CharField(label='Отель или город', required=False)
    room_type = forms.ChoiceField(label='Тип номера', choices=[('', 'Все типы')] + Room.TYPES, required=False)
    capacity = forms.IntegerField(label='Гостей', min_value=1, required=False)
    max_price = forms.DecimalField(label='До, ₽ за ночь', min_value=1, required=False)
    arrival = forms.DateField(label='Заезд', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    departure = forms.DateField(label='Выезд', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def clean(self):
        data = super().clean()
        a, d = data.get('arrival'), data.get('departure')
        if bool(a) != bool(d):
            raise forms.ValidationError('Для проверки свободных номеров укажите обе даты.')
        if a and d and (a < timezone.localdate() or d <= a):
            raise forms.ValidationError('Выберите будущий период, выезд — после заезда.')
        return data


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['arrival', 'departure', 'guests']
        widgets = {name: forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}) for name in ['arrival', 'departure']}

    def clean_arrival(self):
        value = self.cleaned_data['arrival']
        if value < timezone.localdate():
            raise forms.ValidationError('Нельзя бронировать даты в прошлом.')
        return value


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {'text': forms.Textarea(attrs={'rows': 5}), 'rating': forms.NumberInput(attrs={'min': 1, 'max': 10})}
