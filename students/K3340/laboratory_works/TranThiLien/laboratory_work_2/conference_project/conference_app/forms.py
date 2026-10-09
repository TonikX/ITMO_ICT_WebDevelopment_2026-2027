from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Registration, Review, Conference


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['report_title', 'abstract']
        labels = {
            'report_title': 'Название доклада',
            'abstract': 'Аннотация',
        }
        widgets = {
            'report_title': forms.TextInput(attrs={
                'placeholder': 'Введите название доклада',
                'class': 'form-control',
            }),
            'abstract': forms.Textarea(attrs={
                'placeholder': 'Краткое содержание доклада',
                'rows': 6,
                'class': 'form-control',
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        labels = {
            'text': 'Текст отзыва',
            'rating': 'Оценка (1–10)',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Поделитесь впечатлениями о конференции',
                'rows': 6,
                'class': 'form-control',
            }),
            'rating': forms.Select(attrs={'class': 'form-control'}),
        }


class ConferenceForm(forms.ModelForm):
    class Meta:
        model = Conference
        fields = ['title', 'topics', 'venue', 'start_date', 'end_date',
                  'description', 'venue_desc', 'conditions']

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    """Form đăng ký user mới — kế thừa UserCreationForm của Django"""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'password1', 'password2']