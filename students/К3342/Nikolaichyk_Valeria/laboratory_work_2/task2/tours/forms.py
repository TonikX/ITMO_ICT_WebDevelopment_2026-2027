from django import forms
from .models import Booking, Review


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['places']
        labels = {'places': 'Количество мест',}
        widgets = {'places': forms.NumberInput(attrs={'class': 'form-control','min': 1,}),}

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            'travel_start_date',
            'travel_end_date',
            'text',
            'rating',
        ]

        labels = {
            'travel_start_date': 'Дата начала поездки',
            'travel_end_date': 'Дата окончания поездки',
            'text': 'Ваш отзыв',
            'rating': 'Оценка (от 1 до 10)',
        }

        widgets = {
            'travel_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'travel_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),}


    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get('travel_start_date')
        end_date = cleaned_data.get('travel_end_date')

        if start_date and end_date and end_date < start_date:
            self.add_error(
                'travel_end_date',
                'Дата окончания не может быть раньше даты начала.'
            )

        return cleaned_data