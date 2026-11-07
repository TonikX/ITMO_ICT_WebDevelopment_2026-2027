from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CarOwner(AbstractUser):
    birth_date = models.DateTimeField(null=True, blank=True)
    passport_number = models.CharField(max_length=10, blank=True)
    home_address = models.TextField(blank=True)
    nationality = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

class Car(models.Model):
    registration_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30, null=True, blank=True)
    owners = models.ManyToManyField(CarOwner, through="Ownership")

    def __str__(self):
        return f"{self.brand} {self.model} {self.registration_number}"

class Ownership(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.owner} — {self.car}"

class DriverLicense(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE)
    number = models.CharField(max_length=10)
    license_type = models.CharField(max_length=10)
    issue_date = models.DateTimeField()

    def __str__(self):
        return f"{self.number} — {self.owner}"