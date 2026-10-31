
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    passport_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    nationality = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Car(models.Model):
    id_car = models.AutoField(primary_key=True)
    car_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30)
    owners = models.ManyToManyField(
        User,
        through='Ownership',
        related_name='cars'
    )

    def __str__(self):
        return self.brand + ' ' + self.model


class Ownership(models.Model):
    id_ownership = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        null=True
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.owner) + ' - ' + str(self.car)


class DrivingLicense(models.Model):
    id_license = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=10)
    license_type = models.CharField(max_length=10)
    issue_date = models.DateTimeField()

    def __str__(self):
        return self.license_number
