from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Registration, Race


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'team',
            'experience',
            'driver_class',
            'bio',
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'team': forms.TextInput(attrs={'class': 'form-control'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'driver_class': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ('car_description',)
        widgets = {
            'car_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Опишите автомобиль, на котором выступаете',
            }),
        }

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', 'comment_type', 'rating')
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ваш комментарий',
            }),
            'comment_type': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
            }),
        }

class RaceForm(forms.ModelForm):
    class Meta:
        model = Race
        fields = ('name', 'location', 'date', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ResultForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ('race_time', 'result')
        widgets = {
            'race_time': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 1:40:33.843',
            }),
            'result': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 1 место',
            }),
        }