from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.


class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    home_address = models.CharField(max_length=255, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    cars = models.ManyToManyField('Car', through='DriverCar', related_name='owners')


class Car(models.Model):
    number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30)


class DriverLicense(models.Model):
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    number = models.CharField(max_length=10)
    type = models.CharField(max_length=10)
    received_at = models.DateField(null=False)


class DriverCar(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    started_at = models.DateField()
    ended_at = models.DateField()

