from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    passport = models.CharField(max_length=8, blank=True)
    home_address = models.CharField(max_length=100, blank=True)
    nationality = models.CharField(max_length=40, blank=True)
    birthday = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=1, blank=True)
    # для логов
    def __str__(self):
        if self.last_name or self.first_name:
            return f"{self.last_name} {self.first_name}"
        return self.username

class Car(models.Model):
    license_plate = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30, null=True, blank=True)

    owners = models.ManyToManyField(User, through='Ownership')

    def __str__(self):
        return f"Автомобиль {self.brand} с номером {self.license_plate}"




class DrivingLicence(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=10)
    type = models.CharField(max_length=10)
    date = models.DateField()

    def __str__(self):
        return f"Права {self.license_number} ({self.owner.last_name})"


class Ownership(models.Model):
    '''many:many'''
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, null=True, blank = True, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_end = models.DateField(null=True, blank = True)

    def __str__(self):
        return f"{self.owner.first_name} {self.owner.last_name} владеет {self.car.model} номер {self.car.license_plate}"