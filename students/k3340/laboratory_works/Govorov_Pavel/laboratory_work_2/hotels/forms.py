from django import forms
from django.utils import timezone

from .models import Booking, Review, Room


class RoomFilterForm(forms.Form):
    q = forms.CharField(
        label="Поиск",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Отель, адрес, удобства"}),
    )
    room_type = forms.ChoiceField(
        label="Тип номера",
        choices=[("", "Любой тип"), *Room.Type.choices],
        required=False,
    )
    capacity = forms.IntegerField(label="Гостей, не менее", min_value=1, required=False)
    max_price = forms.DecimalField(
        label="Цена до, ₽ / ночь",
        min_value=1,
        max_digits=9,
        decimal_places=2,
        required=False,
    )


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["arrival", "departure", "guests"]
        widgets = {
            name: forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})
            for name in ["arrival", "departure"]
        }

    def clean_arrival(self):
        arrival = self.cleaned_data["arrival"]
        if not self.instance.pk and arrival < timezone.localdate():
            raise forms.ValidationError("Нельзя забронировать номер на прошедшую дату.")
        return arrival


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["arrival", "departure", "rating", "text"]
        widgets = {
            "arrival": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "departure": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "text": forms.Textarea(attrs={"rows": 4}),
            "rating": forms.NumberInput(attrs={"min": 1, "max": 10}),
        }
