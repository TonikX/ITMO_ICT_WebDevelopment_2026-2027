from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=12, blank=True)
    home_address = models.CharField(max_length=200, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    cars = models.ManyToManyField("Car", through="Ownership")

    def __str__(self):
        return self.get_full_name() or self.username


class Car(models.Model):
    state_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.brand, self.model)


class Ownership(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.owner, self.car)


class DriverLicense(models.Model):
    LICENSE_TYPES = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
        ("M", "M"),
    ]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=10)
    license_type = models.CharField(max_length=1, choices=LICENSE_TYPES)
    issue_date = models.DateField()

    def __str__(self):
        return "{} ({})".format(self.license_number, self.license_type)
