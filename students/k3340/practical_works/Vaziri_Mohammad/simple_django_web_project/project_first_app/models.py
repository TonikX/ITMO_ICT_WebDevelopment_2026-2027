"""Модель данных об автовладельцах (практики 2.1–2.3).

Owner — автовладелец и одновременно пользователь системы (практика 2.3,
расширение AbstractUser). Car связан с Owner связью «многие ко многим» через
ассоциативную сущность Ownership (практика 2.2), у которой есть свои атрибуты:
даты начала и конца владения.
"""
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse


class Owner(AbstractUser):
    """Автовладелец. Фамилия и имя берутся из AbstractUser (last_name, first_name)."""

    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    passport_number = models.CharField("Номер паспорта", max_length=20, blank=True)
    home_address = models.CharField("Домашний адрес", max_length=255, blank=True)
    nationality = models.CharField("Национальность", max_length=50, blank=True)

    class Meta:
        verbose_name = "Автовладелец"
        verbose_name_plural = "Автовладельцы"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}".strip()
        return full_name or self.username

    def get_absolute_url(self):
        return reverse("owner_detail", args=[self.pk])


class Car(models.Model):
    plate_number = models.CharField("Гос. номер", max_length=15, unique=True)
    brand = models.CharField("Марка", max_length=20)
    model = models.CharField("Модель", max_length=20)
    color = models.CharField("Цвет", max_length=30, blank=True)
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Ownership",
        related_name="cars",
        verbose_name="Владельцы",
    )

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ["brand", "model"]

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"

    def get_absolute_url(self):
        return reverse("car_detail", args=[self.pk])


class Ownership(models.Model):
    """Ассоциативная сущность «Владение»."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ownerships",
        verbose_name="Владелец",
    )
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE, related_name="ownerships", verbose_name="Автомобиль"
    )
    start_date = models.DateField("Дата начала владения")
    end_date = models.DateField("Дата конца владения", null=True, blank=True)

    class Meta:
        verbose_name = "Владение"
        verbose_name_plural = "Владения"
        ordering = ["car", "start_date"]

    def __str__(self):
        end = self.end_date or "по н. в."
        return f"{self.owner} — {self.car}: {self.start_date} … {end}"

    def clean(self):
        """Периоды владения одним автомобилем не должны пересекаться."""
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("Дата конца владения раньше даты начала.")
        if not self.car_id or not self.start_date:
            return
        others = Ownership.objects.filter(car_id=self.car_id).exclude(pk=self.pk)
        # пересечение: другой период начался до нашего конца и закончился после нашего начала
        if self.end_date:
            others = others.filter(start_date__lte=self.end_date)
        overlap = others.filter(Q(end_date__isnull=True) | Q(end_date__gte=self.start_date))
        if overlap.exists():
            raise ValidationError("Период владения пересекается с другим владением этим автомобилем.")


class DriverLicense(models.Model):
    LICENSE_TYPES = [
        ("A", "A — мотоциклы"),
        ("B", "B — легковые автомобили"),
        ("C", "C — грузовые автомобили"),
        ("D", "D — автобусы"),
        ("BE", "BE — легковые с прицепом"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="licenses",
        verbose_name="Владелец",
    )
    license_number = models.CharField("Номер удостоверения", max_length=10, unique=True)
    license_type = models.CharField("Тип", max_length=10, choices=LICENSE_TYPES)
    issue_date = models.DateField("Дата выдачи")

    class Meta:
        verbose_name = "Водительское удостоверение"
        verbose_name_plural = "Водительские удостоверения"

    def __str__(self):
        return f"{self.license_number} ({self.license_type})"
