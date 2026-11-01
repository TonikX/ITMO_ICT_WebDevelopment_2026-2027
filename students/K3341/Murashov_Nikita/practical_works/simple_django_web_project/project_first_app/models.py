from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CarOwner(AbstractUser):
    """Автовладелец. last_name / first_name — стандартные поля AbstractUser."""

    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    passport_number = models.CharField("Номер паспорта", max_length=20, blank=True)
    home_address = models.CharField("Домашний адрес", max_length=200, blank=True)
    nationality = models.CharField("Национальность", max_length=50, blank=True)

    class Meta:
        verbose_name = "автовладелец"
        verbose_name_plural = "автовладельцы"

    def __str__(self):
        return self.get_full_name() or self.username


class Car(models.Model):
    state_number = models.CharField("Гос. номер", max_length=15)
    brand = models.CharField("Марка", max_length=20)
    model = models.CharField("Модель", max_length=20)
    color = models.CharField("Цвет", max_length=30, blank=True)
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Ownership", related_name="cars", verbose_name="Владельцы"
    )

    class Meta:
        ordering = ["state_number"]
        verbose_name = "автомобиль"
        verbose_name_plural = "автомобили"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.state_number})"


class Ownership(models.Model):
    """Владение: у связи есть даты, поэтому M2M идёт через промежуточную модель."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ownerships", verbose_name="Владелец"
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="ownerships", verbose_name="Автомобиль")
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания", null=True, blank=True)

    class Meta:
        ordering = ["start_date"]
        verbose_name = "владение"
        verbose_name_plural = "владения"

    def __str__(self):
        return f"{self.owner}: {self.car} с {self.start_date}"


class DriverLicense(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="licenses", verbose_name="Владелец"
    )
    license_number = models.CharField("Номер удостоверения", max_length=10)
    type = models.CharField("Тип", max_length=10)
    issue_date = models.DateField("Дата выдачи")

    class Meta:
        verbose_name = "водительское удостоверение"
        verbose_name_plural = "водительские удостоверения"

    def __str__(self):
        return f"{self.license_number} ({self.type})"
