from django import forms
from .models import Registration, Feedback


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['name', 'description', 'topics']
        labels = {
            'name': 'Название доклада',
            'description': 'Аннотация',
            'topics': 'Тематики',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'topics': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, conference=None, **kwargs):
        super().__init__(*args, **kwargs)
        if conference is not None:
            self.fields['topics'].queryset = conference.topics.all()


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['text', 'rating']
        labels = {
            'text': 'Ваш отзыв',
            'rating': 'Оценка (от 1 до 10)',
        }
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)