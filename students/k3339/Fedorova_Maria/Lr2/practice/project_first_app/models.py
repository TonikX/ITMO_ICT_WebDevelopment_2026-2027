from django.contrib.auth.models import AbstractUser
from django.db import models


class CarOwner(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    home_address = models.CharField(max_length=255, blank=True)
    nationality = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.username


class Car(models.Model):
    state_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    owners = models.ManyToManyField(
        CarOwner,
        through="Ownership",
        related_name="cars",
    )

    def __str__(self) -> str:
        return f"{self.brand} {self.model} ({self.state_number})"


class Ownership(models.Model):
    owner = models.ForeignKey(
        CarOwner,
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

    def __str__(self) -> str:
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
        CarOwner,
        on_delete=models.CASCADE,
        related_name="licenses",
    )
    license_number = models.CharField(max_length=20)
    license_type = models.CharField(max_length=2, choices=LICENSE_TYPES)
    issue_date = models.DateField()

    def __str__(self) -> str:
        return f"{self.license_number} ({self.license_type})"
