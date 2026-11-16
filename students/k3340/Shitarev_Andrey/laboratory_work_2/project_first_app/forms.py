from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Driver, Race, Registration, Comment

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',)

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        exclude = ('user',)

class RaceForm(forms.ModelForm):
    class Meta:
        model = Race
        fields = ('name', 'date', 'place', 'description')

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ('note',)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('run_date', 'text', 'comment_type', 'rating')
