from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Registration, Comment, Result, Auto


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            w = field.widget
            if isinstance(w, forms.CheckboxInput):
                cls = "form-check-input"
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                cls = "form-select"
            else:
                cls = "form-control"
            w.attrs["class"] = (w.attrs.get("class", "") + " " + cls).strip()


class UserRegistrationForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email","team", "birthday", "driving_experience", "racer_class")


class UserProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email","team", "birthday", "driving_experience", "racer_class")
        widgets = {
            "birthday": forms.DateInput(attrs={"type": "date"}),
        }


class RaceRegistrationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Registration
        fields = ("race", )


class CommentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text", "race_date", "comment_type", "rating")
        widgets = {
            "race_date": forms.DateInput(attrs={"type": "date"}),
            "text": forms.Textarea(attrs={"rows": 4}),
        }


class ResultForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Result
        fields = ("user", "auto", "duration")
        widgets = {
            "duration": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "ЧЧ:ММ:СС, например 00:12:34",
            }),
            "user": forms.Select(attrs={"class": "form-select", "id": "id_user"}),
            "auto": forms.Select(attrs={"class": "form-select", "id": "id_auto"}),
        }

    def __init__(self, *args, race=None, user_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Участники — только зарегавшиеся на ЭТУ гонку
        if race is not None:
            self.fields["user"].queryset = User.objects.filter(
                registrations__race=race,
                registrations__deleted_at__isnull=True,
            ).distinct().order_by("last_name", "first_name")
        else:
            self.fields["user"].queryset = User.objects.none()
        self.fields["user"].empty_label = "— выберите участника —"

        # Машины — только выбранного участника
        if user_id:
            autos = Auto.objects.filter(owner_id=user_id, deleted_at__isnull=True)
        else:
            autos = Auto.objects.none()
        self.fields["auto"].queryset = autos
        if autos.count() == 1:
            self.fields["auto"].initial = autos.first()
        self.fields["auto"].empty_label = "— сначала выберите участника —"


class AutoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Auto
        fields = ("state", "make", "model", "color")
        widgets = {
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "А123БВ777"}),
            "make": forms.TextInput(attrs={"class": "form-control", "placeholder": "Toyota"}),
            "model": forms.TextInput(attrs={"class": "form-control", "placeholder": "Supra"}),
            "color": forms.TextInput(attrs={"class": "form-control", "placeholder": "Красный"}),
        }
