from __future__ import annotations

from typing import Any
from django import forms
from django.db.models import QuerySet

from .models import Flight, Passenger, Passport, Review, Ticket, User


class BootstrapFormMixin:
    """
    Миксин, который автоматически добавляет CSS-классы Bootstrap 5
    ко всем полям формы при её инициализации.
    """
    fields: dict[str, forms.Field]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class UserCreationForm(BootstrapFormMixin, forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Введите надежный пароль"}),
        min_length=8,
    )

    class Meta:
        model = User
        fields = ["username", "email", "phone_number", "password"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["phone_number"].required = False

    def save(self, commit: bool = True) -> User:
        user: User = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class NewPassengerInlineForm(BootstrapFormMixin, forms.ModelForm):
    passport_number = forms.CharField(
        label="Номер паспорта",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "Серия и номер (например, 4012 345678)"}),
    )

    class Meta:
        model = Passenger
        fields = ["first_name", "last_name", "birth_date"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Иван"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Иванов"}),
            "birth_date": forms.DateInput(
                format="%d.%m.%Y",
                attrs={"placeholder": "ДД.ММ.ГГГГ"},
            ),
        }

    def clean_passport_number(self) -> str:
        passport_number: str = self.cleaned_data["passport_number"].strip()
        if Passport.objects.filter(passport_number=passport_number).exists():
            raise forms.ValidationError("Паспорт с таким номером уже зарегистрирован в системе.")
        return passport_number


class ReservationUpdateForm(BootstrapFormMixin, forms.Form):
    """Форма редактирования существующего резервирования (состав пассажиров на рейсе)."""
    passengers = forms.ModelMultipleChoiceField(
        queryset=Passenger.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Пассажиры в этой брони",
    )

    def __init__(
        self,
        *args: Any,
        user: User | None = None,
        flight: Flight | None = None,
        current_reservation_id: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        if user and flight:
            # Доступны пассажиры пользователя с активным паспортом, которые либо не имеют
            # билета на этот рейс, либо уже входят в текущую редактируемую бронь
            qs: QuerySet[Passenger] = (
                Passenger.objects.filter(owner=user, passports__is_active=True)
                .exclude(
                    tickets__flight=flight,
                    tickets__reservation_id__in=(
                        Flight.objects.none()
                        if not current_reservation_id
                        else Flight.objects.exclude(reservations__id=current_reservation_id)
                    ),
                )
                .distinct()
            )
            self.fields["passengers"].queryset = qs


class ReviewForm(BootstrapFormMixin, forms.ModelForm):
    """Форма добавления отзыва к рейсу (Рейтинг 1-10 по заданию варианта)."""
    class Meta:
        model = Review
        fields = ["rating", "flight_date", "text"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 10, "placeholder": "От 1 до 10"}),
            "flight_date": forms.DateInput(
                format="%d.%m.%Y",
                attrs={"placeholder": "ДД.ММ.ГГГГ"},
            ),
            "text": forms.Textarea(attrs={"rows": 3, "placeholder": "Поделитесь впечатлениями о перелете..."}),
        }


class StaffTicketCheckInForm(BootstrapFormMixin, forms.ModelForm):
    """
    Форма для сотрудника аэропорта (is_staff) в клиентском интерфейсе:
    позволяет зарегистрировать пассажира на рейс и вписать номер билета.
    """
    class Meta:
        model = Ticket
        fields = ["seat_number", "ticket_number", "is_checked_in"]
        widgets = {
            "ticket_number": forms.TextInput(attrs={"placeholder": "Например, SU-987654321"}),
        }