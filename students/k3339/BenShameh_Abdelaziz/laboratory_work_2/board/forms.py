from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Submission


class SignUpForm(UserCreationForm):
    """
    UserCreationForm is Django's built-in form for registering a new user
    (username + password + password confirmation, with validation already
    wired up). We just tell it which model and fields to use.
    """
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email']  # password1/password2 are added automatically


class SubmissionForm(forms.ModelForm):
    """
    A student only ever types the answer text — homework and student
    are filled in by the view itself, not by the user, so they're not
    listed here.
    """
    class Meta:
        model = Submission
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 6, 'class': 'form-control'}),
        }
