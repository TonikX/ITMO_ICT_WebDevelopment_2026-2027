from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, NumberInput, Textarea

from .models import Registration, Review


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ("first_name", "last_name", "email"):
            self.fields[field].required = True


class RegistrationForm(ModelForm):
    class Meta:
        model = Registration
        fields = ["presentation_title", "affiliation", "abstract"]
        widgets = {"abstract": Textarea(attrs={"rows": 5})}


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        widgets = {"rating": NumberInput(attrs={"min": 1, "max": 10}), "text": Textarea(attrs={"rows": 5})}


class ResultForm(ModelForm):
    class Meta:
        model = Registration
        fields = ["result"]
