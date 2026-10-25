from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    date_of_birth = models.DateTimeField(null=True, blank=True)
    passport_number = models.CharField(max_length=10)
    home_address = models.CharField(max_length=255)
    nationality = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Car(models.Model):
    state_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30, null=True, blank=True)

    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Possession"
    )

    def __str__(self):
        return f"{self.brand} {self.model}"


class Possession(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)