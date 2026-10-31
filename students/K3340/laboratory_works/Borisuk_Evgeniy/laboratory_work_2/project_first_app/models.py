"""Учебная модель автовладельцев из практик 2.1–2.3."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """Пользователь с атрибутами автовладельца."""

    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    passport_number = models.CharField("Номер паспорта", max_length=20, blank=True)
    address = models.CharField("Домашний адрес", max_length=250, blank=True)
    nationality = models.CharField("Национальность", max_length=100, blank=True)

    class Meta(AbstractUser.Meta):
        abstract = False
        constraints = [
            models.CheckConstraint(
                check=models.Q(passport_number="") | models.Q(birth_date__isnull=False),
                name="owner_requires_birth_date",
            )
        ]

    def clean(self) -> None:
        """Сохраняет обязательные данные пользователя, связанного с автомобилем."""
        super().clean()
        has_owner_records = self.pk and (
            self.ownership_set.exists() or self.driverlicense_set.exists()
        )
        if self.passport_number or has_owner_records:
            self.validate_owner_fields()

    def validate_owner_fields(self) -> None:
        """Проверяет обязательные поля перед назначением владельцем."""
        required = [
            "first_name",
            "last_name",
            "birth_date",
            "passport_number",
            "address",
            "nationality",
        ]
        errors = {}
        for name in required:
            value = getattr(self, name)
            if not value or isinstance(value, str) and not value.strip():
                errors[name] = "Укажите данные автовладельца."
        if errors:
            raise ValidationError(errors)


class Car(models.Model):
    """Автомобиль, связанный с владельцами через историю владения."""

    plate_number = models.CharField("Госномер", max_length=15, unique=True)
    brand = models.CharField("Марка", max_length=20)
    model_name = models.CharField("Модель", max_length=20)
    color = models.CharField("Цвет", max_length=30, blank=True)
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Ownership",
        related_name="cars",
        verbose_name="Владельцы",
    )

    class Meta:
        ordering = ["pk"]
        verbose_name = "автомобиль"
        verbose_name_plural = "автомобили"

    def __str__(self) -> str:
        return f"{self.brand} {self.model_name} ({self.plate_number})"


class Ownership(models.Model):
    """Период владения автомобилем без пересечений."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")
    start_date = models.DateField("Начало владения")
    end_date = models.DateField("Окончание владения", null=True, blank=True)

    class Meta:
        ordering = ["start_date", "pk"]
        verbose_name = "владение"
        verbose_name_plural = "владения"
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__isnull=True)
                | models.Q(end_date__gte=models.F("start_date")),
                name="ownership_date_order",
            )
        ]

    def clean(self) -> None:
        if self.owner_id:
            try:
                self.owner.validate_owner_fields()
            except ValidationError as error:
                raise ValidationError(
                    {
                        "owner": "Сначала заполните все обязательные данные автовладельца."
                    }
                ) from error
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "Окончание раньше начала владения."})
        if not self.car_id or not self.start_date:
            return
        periods = Ownership.objects.filter(car_id=self.car_id).exclude(pk=self.pk)
        periods = periods.filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=self.start_date)
        )
        if self.end_date:
            periods = periods.filter(start_date__lte=self.end_date)
        if periods.exists():
            raise ValidationError(
                "Периоды владения одним автомобилем не должны пересекаться."
            )

    def __str__(self) -> str:
        return f"{self.owner} — {self.car}"


class DriverLicense(models.Model):
    """Водительское удостоверение владельца."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )
    number = models.CharField("Номер удостоверения", max_length=10, unique=True)
    category = models.CharField(
        "Категория",
        max_length=10,
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
    )
    issue_date = models.DateField("Дата выдачи")

    class Meta:
        verbose_name = "водительское удостоверение"
        verbose_name_plural = "водительские удостоверения"

    def clean(self) -> None:
        if self.owner_id:
            try:
                self.owner.validate_owner_fields()
            except ValidationError as error:
                raise ValidationError(
                    {
                        "owner": "Сначала заполните все обязательные данные автовладельца."
                    }
                ) from error

    def __str__(self) -> str:
        return self.number
