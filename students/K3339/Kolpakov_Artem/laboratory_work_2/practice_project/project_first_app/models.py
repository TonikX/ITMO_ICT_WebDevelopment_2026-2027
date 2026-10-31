from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    passport_number = models.CharField("Номер паспорта", max_length=20)
    home_address = models.CharField("Домашний адрес", max_length=255)
    nationality = models.CharField("Национальность", max_length=50)

    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "passport_number",
        "home_address",
        "nationality",
    ]

    def __str__(self):
        return self.get_full_name() or self.username


class DriverLicense(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_licenses",
        verbose_name="Владелец",
    )
    number = models.CharField("Номер удостоверения", max_length=10)
    category = models.CharField("Категория", max_length=10)
    issue_date = models.DateField("Дата выдачи")

    class Meta:
        verbose_name = "Водительское удостоверение"
        verbose_name_plural = "Водительские удостоверения"

    def __str__(self):
        return f"{self.number}, категория {self.category}"


class Car(models.Model):
    registration_number = models.CharField("Государственный номер", max_length=15)
    brand = models.CharField("Марка", max_length=20)
    model_name = models.CharField("Модель", max_length=20)
    color = models.CharField("Цвет", max_length=30)
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Ownership",
        related_name="cars",
        verbose_name="Владельцы",
    )

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.registration_number})"


class Ownership(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ownerships",
        verbose_name="Владелец",
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="ownerships",
        verbose_name="Автомобиль",
    )
    start_date = models.DateField("Дата начала владения")
    end_date = models.DateField("Дата окончания владения", null=True, blank=True)

    class Meta:
        verbose_name = "Владение"
        verbose_name_plural = "Владения"

    def __str__(self):
        return f"{self.owner} — {self.car}"
