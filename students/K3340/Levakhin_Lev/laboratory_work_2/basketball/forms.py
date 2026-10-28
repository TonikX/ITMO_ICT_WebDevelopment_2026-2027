from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import CustomUser, Prediction, Comment, Match

INPUT_CLASSES = "w-full bg-neutral-900 border border-neutral-700 text-white px-4 py-3 rounded-sm focus:outline-none focus:border-red-600 transition"


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'display_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': INPUT_CLASSES})


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': INPUT_CLASSES})


class PredictionForm(forms.ModelForm):
    class Meta:
        model = Prediction
        fields = ['predicted_home_score', 'predicted_away_score']
        labels = {
            'predicted_home_score': 'Очки хозяев',
            'predicted_away_score': 'Очки гостей',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': INPUT_CLASSES})


class CommentForm(forms.ModelForm):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 11)]
    rating = forms.ChoiceField(choices=RATING_CHOICES, label="Оценка (1-10)")

    class Meta:
        model = Comment
        fields = ['text', 'rating']
        labels = {'text': 'Текст отзыва'}
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': INPUT_CLASSES})


class MatchStatusForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['status', 'home_score', 'away_score']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': INPUT_CLASSES})
