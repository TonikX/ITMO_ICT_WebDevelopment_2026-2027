from django.contrib.auth.models import AbstractUser
from django.db import models

class CarOwner(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    passport = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

class Car(models.Model):
    plate_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model_name = models.CharField(max_length=20)
    color = models.CharField(max_length=30, null=True, blank=True)
    owners = models.ManyToManyField(CarOwner, through='Ownership')

    def __str__(self):
        return f'{self.brand} {self.model_name} ({self.plate_number})'


class Ownership(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.owner} - {self.car}'

class DriverLicense(models.Model):
    LICENSE_TYPE = (
        ('A', 'Мотоцикл'),
        ('B', 'Легковой автомобиль'),
        ('C', 'Грузовой автомобиль'),
        ('D', 'Автобус'),
        ('E', 'Прицеп'),
    )

    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=10)
    license_type = models.CharField(max_length=10, choices=LICENSE_TYPE)
    issue_date = models.DateField()

    def __str__(self):
        return f'{self.license_type} {self.license_number}'