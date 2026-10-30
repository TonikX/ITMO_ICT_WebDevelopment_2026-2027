from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CarOwner


def _without_help_text(form: forms.BaseForm) -> None:
    for field in form.fields.values():
        field.help_text = ""


def _setup_birth_date(form: forms.BaseForm) -> None:
    if "birth_date" not in form.fields:
        return
    form.fields["birth_date"].required = False
    form.fields["birth_date"].widget = forms.DateInput(
        attrs={"type": "date"},
        format="%Y-%m-%d",
    )
    form.fields["birth_date"].input_formats = ["%Y-%m-%d"]


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _without_help_text(self)


class CarOwnerForm(forms.ModelForm):
    class Meta:
        model = CarOwner
        fields = [
            "username",
            "first_name",
            "last_name",
            "birth_date",
            "passport_number",
            "home_address",
            "nationality",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _without_help_text(self)
        _setup_birth_date(self)


class CarOwnerUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CarOwner
        fields = (
            "username",
            "first_name",
            "last_name",
            "birth_date",
            "passport_number",
            "home_address",
            "nationality",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _without_help_text(self)
        _setup_birth_date(self)
