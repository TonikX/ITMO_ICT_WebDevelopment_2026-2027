from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import RaceComment, RaceEntry, RaceResult, User


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class RaceEntryForm(forms.ModelForm):
    class Meta:
        model = RaceEntry
        fields = (
            "full_name",
            "team_name",
            "car_description",
            "participant_description",
            "experience",
            "racer_class",
        )


class RaceCommentForm(forms.ModelForm):
    class Meta:
        model = RaceComment
        fields = ("race_date", "text", "comment_type", "rating")


class RaceResultForm(forms.ModelForm):
    class Meta:
        model = RaceResult
        fields = ("entry", "finish_time", "place", "notes")

    def __init__(self, *args, race=None, **kwargs):
        super().__init__(*args, **kwargs)
        if race is not None:
            self.fields["entry"].queryset = RaceEntry.objects.filter(race=race)
