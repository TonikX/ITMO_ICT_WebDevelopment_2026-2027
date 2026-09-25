from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CarOwner(AbstractUser):
    passport_number = models.CharField(max_length=20, blank=True)
    home_address = models.CharField(max_length=200, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username


class Car(models.Model):
    license_plate = models.CharField(max_length=15)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=30, null=True, blank=True)
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Ownership",
        related_name="cars",
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.license_plate})"


class Ownership(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ownerships",
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="ownerships",
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.owner} — {self.car}"


class DriverLicense(models.Model):
    LICENSE_TYPES = (
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
        ("E", "E"),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="licenses",
    )
    license_number = models.CharField(max_length=20)
    license_type = models.CharField(max_length=2, choices=LICENSE_TYPES)
    issue_date = models.DateField()

    def __str__(self):
        return f"{self.license_number} ({self.license_type})"
