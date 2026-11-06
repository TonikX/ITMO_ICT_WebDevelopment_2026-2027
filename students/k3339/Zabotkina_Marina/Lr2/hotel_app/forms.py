from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Booking, Review, User


class RegisterForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "passport_series",
            "passport_number",
            "phone_number",
            "home_address",
            "nationality",
            "birth_date",
        )
        widgets = {"birth_date": forms.DateInput(attrs={"type": "date"})}


class BookingForm(forms.ModelForm):
    first_name = forms.CharField(label="Имя гостя", required=False)
    last_name = forms.CharField(label="Фамилия гостя", required=False)
    phone_number = forms.CharField(label="Контактный телефон", required=False)

    class Meta:
        model = Booking
        fields = [
            "check_in_date",
            "check_out_date",
            "guests_count",
            "first_name",
            "last_name",
            "phone_number",
        ]
        widgets = {
            "check_in_date": forms.DateInput(attrs={"type": "date"}),
            "check_out_date": forms.DateInput(attrs={"type": "date"}),
            "guests_count": forms.NumberInput(attrs={"min": 1, "max": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["phone_number"].initial = (self.instance.user.phone_number)

    def save(self, commit=True):
        booking = super().save(commit=commit)
        if booking.user:
            user = booking.user
            user.first_name = self.cleaned_data.get("first_name", user.first_name)
            user.last_name = self.cleaned_data.get("last_name", user.last_name)
            user.phone_number = self.cleaned_data.get("phone_number", user.phone_number)
            user.save()
        return booking


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ["stay_period", "rating", "text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Поделитесь впечатлениями об удобстве, чистоте...",
                }
            ),
        }