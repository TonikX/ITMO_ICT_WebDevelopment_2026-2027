from django import forms
from .models import Comment, Registration


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['full_name', 'team', 'car_description', 'description', 'experience', 'driver_class']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'comment_type', 'rating']


class ResultForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['race_time', 'result']
        help_texts = {'race_time': 'Формат: ЧЧ:ММ:СС, например 00:02:15.'}
