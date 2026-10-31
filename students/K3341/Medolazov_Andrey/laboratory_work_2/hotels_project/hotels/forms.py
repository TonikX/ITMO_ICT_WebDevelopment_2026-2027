from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Reservation, Review


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'


class RegisterForm(BootstrapMixin, UserCreationForm):
    first_name = forms.CharField(label='Имя', max_length=150)
    last_name = forms.CharField(label='Фамилия', max_length=150)
    email = forms.EmailField(label='Email')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ReservationForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date_from', 'date_to', 'guests']
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'date_to': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, room=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.room = room or self.instance.room

    def clean(self):
        cleaned = super().clean()
        date_from = cleaned.get('date_from')
        date_to = cleaned.get('date_to')
        guests = cleaned.get('guests')

        if date_from and date_from < timezone.localdate():
            self.add_error('date_from', 'Нельзя бронировать на прошедшие даты')
        if date_from and date_to and date_to <= date_from:
            self.add_error('date_to', 'Дата выезда должна быть позже даты заезда')
        if guests and guests > self.room.capacity:
            self.add_error('guests', f'Номер рассчитан максимум на {self.room.capacity} гостей')

        if date_from and date_to and not self.errors:
            busy = Reservation.objects.filter(
                room=self.room,
                status__in=['booked', 'checked_in'],
                date_from__lt=date_to,
                date_to__gt=date_from,
            ).exclude(pk=self.instance.pk)
            if busy.exists():
                raise forms.ValidationError('Номер уже занят на выбранные даты')
        return cleaned


class ReviewForm(BootstrapMixin, forms.ModelForm):
    rating = forms.TypedChoiceField(
        label='Рейтинг',
        choices=[(i, i) for i in range(10, 0, -1)],
        coerce=int,
    )

    class Meta:
        model = Review
        fields = ['date_from', 'date_to', 'rating', 'text']
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'date_to': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'text': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned = super().clean()
        date_from = cleaned.get('date_from')
        date_to = cleaned.get('date_to')
        if date_from and date_from > timezone.localdate():
            self.add_error('date_from', 'Отзыв можно оставить только о прошедшем проживании')
        if date_from and date_to and date_to < date_from:
            self.add_error('date_to', 'Дата окончания раньше даты начала')
        return cleaned
