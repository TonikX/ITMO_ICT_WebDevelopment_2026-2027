from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class CarOwner(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateTimeField(null=True, blank=True)

    passport_number = models.CharField(max_length=20, blank=True)
    home_address = models.CharField(max_length=200, blank=True)
    nationality = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Car(models.Model):
    plate_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model_name = models.CharField(max_length=20)
    color = models.CharField(max_length=30, null=True, blank=True)

    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Ownership",
        related_name="cars",
        blank=True
    )

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.plate_number})"


class Ownership(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ownership_records"
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="ownership_records"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.owner} - {self.car}"


class DriverLicense(models.Model):
    LICENSE_TYPES = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="licenses"
    )
    license_number = models.CharField(max_length=10)
    license_type = models.CharField(max_length=10, choices=LICENSE_TYPES)
    issue_date = models.DateTimeField()

    def __str__(self):
        return self.license_number
