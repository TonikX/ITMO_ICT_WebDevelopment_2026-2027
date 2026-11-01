from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import RacerUser
from .models import RaceRegistration, Comment


class RacerRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = RacerUser
        # поля пользователя
        fields = ('username', 'full_name', 'team_name', 'racer_class', 'experience')

class RaceEnrollForm(forms.ModelForm):
    class Meta:
        model = RaceRegistration
        fields = ['car_number', 'racer_comment']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_type', 'rating', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }