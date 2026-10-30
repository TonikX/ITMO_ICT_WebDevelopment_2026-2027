from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Participation, Review, User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "organization", "academic_degree"]


class ParticipationForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = ["talk_title", "abstract"]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        widgets = {"rating": forms.NumberInput(attrs={"min": 1, "max": 10})}
