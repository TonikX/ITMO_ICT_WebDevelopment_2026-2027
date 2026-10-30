from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Reservation, Review, Tour
from django.contrib.auth import get_user_model




User = get_user_model()


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('tour', 'participants_count')
        widgets = {
            'tour': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        tour = kwargs.pop('tour', None)
        super().__init__(*args, **kwargs)
        if tour:
            self.fields['tour'].initial = tour


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 11)]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        label='Рейтинг (1–10)'
    )

    class Meta:
        model = Review
        fields = ('text', 'rating')
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Поделитесь впечатлениями о туре...',
                'class': 'form-control',
            }),
        }


class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = (
            'name', 'agency', 'country', 'description',
            'start_date', 'end_date', 'price',
            'payment_terms', 'max_participants', 'image'
        )
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ToursRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User 
        fields = ('username', 'email', 'password1', 'password2')