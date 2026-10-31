from django.db import models
from django.contrib.auth.models import AbstractUser

class CarOwner(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class DriverLicense(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE)
    number = models.CharField(max_length=10)
    type = models.CharField(max_length=10)
    issue_date = models.DateField()

    def __str__(self):
        return f'{self.number} ({self.type})'


class Car(models.Model):
    state_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model_name = models.CharField(max_length=20)
    color = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f'{self.brand} {self.model_name} ({self.state_number})'


class Ownership(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.owner} — {self.car}'

class User(AbstractUser):
    name = models.CharField(max_length=100, blank=True, null=True)
    passport_number = models.CharField(max_length=10, blank=True, null=True)
    home_address = models.CharField(max_length=255, blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)