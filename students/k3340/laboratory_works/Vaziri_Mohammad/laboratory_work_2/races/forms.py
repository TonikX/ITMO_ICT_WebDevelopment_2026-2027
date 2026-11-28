from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Comment, Racer, Registration


class BootstrapMixin:
    """Добавляет виджетам классы Bootstrap."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Select):
                css = "form-select"
            elif isinstance(widget, forms.CheckboxInput):
                css = "form-check-input"
            else:
                css = "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {css}".strip()


class SignUpForm(BootstrapMixin, UserCreationForm):
    first_name = forms.CharField(label="Имя", max_length=150)
    last_name = forms.CharField(label="Фамилия", max_length=150)
    email = forms.EmailField(label="Email")

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "last_name", "first_name", "email")


class RacerForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Racer
        fields = ("full_name", "team", "racer_class", "experience_years", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class RegistrationForm(BootstrapMixin, forms.ModelForm):
    """Регистрация гонщика на гонку. Гонка и гонщик задаются представлением."""

    class Meta:
        model = Registration
        fields = ("car_number", "car_description")
        widgets = {"car_description": forms.TextInput(attrs={"placeholder": "Например: Lada Vesta Sport, 1.8 л, 145 л. с."})}

    def __init__(self, *args, race, racer, **kwargs):
        super().__init__(*args, **kwargs)
        self.race = race
        self.racer = racer
        self.instance.race = race
        self.instance.racer = racer

    def clean(self):
        cleaned = super().clean()
        same_race = Registration.objects.filter(race=self.race)
        if self.instance.pk:
            same_race = same_race.exclude(pk=self.instance.pk)
        if same_race.filter(racer=self.racer).exists():
            raise ValidationError("Вы уже зарегистрированы на эту гонку.")
        number = cleaned.get("car_number")
        if number and same_race.filter(car_number=number).exists():
            self.add_error("car_number", "Этот стартовый номер уже занят другим участником.")
        return cleaned


class CommentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("heat_date", "comment_type", "rating", "text")
        widgets = {
            "heat_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "rating": forms.NumberInput(attrs={"min": 1, "max": 10}),
            "text": forms.Textarea(attrs={"rows": 4}),
        }
