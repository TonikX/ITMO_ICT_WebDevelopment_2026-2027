from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CarOwner(AbstractUser):
    # id = AutoField(primary_key=True) — создаётся Django неявно
    # username/password/email/is_staff/is_superuser и т.п. — от AbstractUser
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    birth_date = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    home_address = models.CharField(max_length=200, blank=True)
    nationality = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Car(models.Model):
    # id = AutoField(primary_key=True) — создаётся Django неявно
    plate_number = models.CharField(max_length=15)
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30, null=True, blank=True)
    owners = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Ownership', related_name='cars')

    def __str__(self):
        return f'{self.brand} {self.model} ({self.plate_number})'


class Ownership(models.Model):
    """Ассоциативная сущность "Владение"."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # FK -> CarOwner.id
    car = models.ForeignKey(Car, on_delete=models.CASCADE)         # FK -> Car.id
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.owner} — {self.car} ({self.start_date}..{self.end_date or ""})'


class DriverLicense(models.Model):
    """Водительское удостоверение."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # FK -> CarOwner.id
    license_number = models.CharField(max_length=10)
    type = models.CharField(max_length=10)
    issue_date = models.DateField()

    def __str__(self):
        return f'{self.license_number} ({self.owner})'
