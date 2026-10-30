from django import forms

from .models import Reservation, Review


class ReservationForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out:
            if check_out <= check_in:
                self.add_error(
                    'check_out',
                    'Дата выезда должна быть позже даты заезда'
                )
            elif self.instance.room_id:
                reservations = Reservation.objects.filter(
                    room_id=self.instance.room_id,
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                ).exclude(pk=self.instance.pk)

                if reservations.exists():
                    raise forms.ValidationError(
                        'Номер уже забронирован на выбранные даты'
                    )

        return cleaned_data

    class Meta:
        model = Reservation
        fields = ['check_in', 'check_out']

        widgets = {
            'check_in': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'check_out': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
        }


class ReviewForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        stay_from = cleaned_data.get('stay_from')
        stay_to = cleaned_data.get('stay_to')

        if stay_from and stay_to and stay_to <= stay_from:
            self.add_error(
                'stay_to',
                'Дата окончания проживания должна быть позже даты начала',
            )

        return cleaned_data

    class Meta:
        model = Review
        fields = ['stay_from', 'stay_to', 'text', 'rating']

        widgets = {
            'stay_from': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'stay_to': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'text': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 10,
            }),
        }