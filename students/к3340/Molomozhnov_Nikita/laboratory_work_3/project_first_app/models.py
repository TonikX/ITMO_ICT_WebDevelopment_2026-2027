from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    passport_number = models.CharField(max_length=20, blank=True)
    home_address = models.TextField(blank=True)
    nationality = models.CharField(max_length=50, blank=True)


class CarOwner(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Car(models.Model):
    state_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model_name = models.CharField(max_length=20)
    color = models.CharField(max_length=30, null=True, blank=True)
    owners = models.ManyToManyField(
        CarOwner, through='Ownership', related_name='cars'
    )

    def __str__(self):
        return f'{self.brand} {self.model_name}'


class Ownership(models.Model):
    owner = models.ForeignKey(
        CarOwner, on_delete=models.CASCADE, related_name='ownerships'
    )
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE, related_name='ownerships'
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.owner} - {self.car}'


class DriverLicense(models.Model):
    owner = models.OneToOneField(
        CarOwner, on_delete=models.CASCADE, related_name='license'
    )
    license_number = models.CharField(max_length=10)
    license_type = models.CharField(max_length=10)
    issue_date = models.DateTimeField()

    def __str__(self):
        return self.license_number
