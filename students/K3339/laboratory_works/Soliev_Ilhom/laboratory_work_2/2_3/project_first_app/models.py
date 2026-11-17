from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    passport_number = models.CharField(max_length=20, blank=True)
    home_address = models.CharField(max_length=255, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

    class Meta:
        verbose_name = "автовладелец"
        verbose_name_plural = "автовладельцы"


class DriverLicense(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="licenses",
    )
    license_number = models.CharField(max_length=10)
    license_type = models.CharField(max_length=10)
    issue_date = models.DateTimeField()

    def __str__(self):
        return self.license_number


class Car(models.Model):
    registration_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30)
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Ownership",
        related_name="cars",
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.registration_number})"


class Ownership(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.owner} — {self.car}"
