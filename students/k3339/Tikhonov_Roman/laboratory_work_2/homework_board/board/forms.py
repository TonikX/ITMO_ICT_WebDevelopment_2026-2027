from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Homework, Submission

User = get_user_model()


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ["subject", "issued", "due", "text", "penalties"]
        widgets = {
            "issued": forms.DateInput(attrs={"type": "date"}),
            "due": forms.DateInput(attrs={"type": "date"}),
            "penalties": forms.Textarea(attrs={"rows": 3}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 8})}
