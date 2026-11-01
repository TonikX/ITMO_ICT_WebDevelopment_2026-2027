from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Conference, Participation, Review, Topic, User
from .services import SORT_OPTIONS
from .validators import RATING_MAX, RATING_MIN


def date_input():
    return forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                css = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
                field.widget.attrs.setdefault("class", css)


class RegisterForm(BootstrapMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "organization", "academic_degree")


class ConferenceForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Conference
        fields = [
            "title", "topics", "venue_name", "city", "start_date", "end_date",
            "description", "venue_description", "participation_terms",
        ]
        widgets = {"start_date": date_input(), "end_date": date_input(), "topics": forms.CheckboxSelectMultiple}


class ParticipationForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Participation
        fields = ["talk_title", "abstract"]


class ResultForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Participation
        fields = ["result"]


class ReviewForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Review
        fields = ["start_date", "end_date", "rating", "text"]
        widgets = {
            "start_date": date_input(),
            "end_date": date_input(),
            "rating": forms.NumberInput(attrs={"min": RATING_MIN, "max": RATING_MAX}),
        }
        help_texts = {"rating": f"От {RATING_MIN} до {RATING_MAX}"}


# Формы-фильтры разбирают параметры адресной строки: всё некорректное (`?date_from=abc`,
# несуществующая тематика, чужой вариант сортировки) просто выпадает из `cleaned_data`.
class ConferenceFilter(forms.Form):
    q = forms.CharField(required=False)
    topic = forms.ModelChoiceField(Topic.objects.all(), required=False)
    city = forms.CharField(required=False)
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)
    sort = forms.ChoiceField(choices=[(key, label) for key, (label, _) in SORT_OPTIONS.items()], required=False)


class ParticipantFilter(forms.Form):
    q = forms.CharField(required=False)
    conference = forms.ModelChoiceField(Conference.objects.all(), required=False)
    result = forms.ChoiceField(choices=Participation.Result.choices, required=False)
