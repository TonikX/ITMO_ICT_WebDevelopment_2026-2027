"""Формы владельца и автомобиля для практик."""

from django import forms

from conferences.forms import SignupForm

from .models import Car


class OwnerForm(SignupForm):
    """Создаёт пользователя с атрибутами автовладельца."""

    class Meta(SignupForm.Meta):
        fields = SignupForm.Meta.fields + [
            "birth_date",
            "passport_number",
            "address",
            "nationality",
        ]
        widgets = {"birth_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for name in [
            "first_name",
            "last_name",
            "birth_date",
            "passport_number",
            "address",
            "nationality",
        ]:
            self.fields[name].required = True


class CarForm(forms.ModelForm):
    """Редактирует поля автомобиля без подмены истории владения."""

    class Meta:
        model = Car
        fields = ["plate_number", "brand", "model_name", "color"]
