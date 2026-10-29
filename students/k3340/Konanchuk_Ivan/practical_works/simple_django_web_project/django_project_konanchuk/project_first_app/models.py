from django.contrib.auth.models import AbstractUser
from django.db import models


class CarOwner(AbstractUser):
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    passport_number = models.CharField("Номер паспорта", max_length=20, blank=True)
    home_address = models.CharField("Домашний адрес", max_length=200, blank=True)
    nationality = models.CharField("Национальность", max_length=50, blank=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Car(models.Model):
    state_number = models.CharField("Гос. номер", max_length=15)
    brand = models.CharField("Марка", max_length=20)
    model = models.CharField("Модель", max_length=20)
    color = models.CharField("Цвет", max_length=30, null=True, blank=True)
    owners = models.ManyToManyField(CarOwner, through="Ownership", related_name="cars")

    def __str__(self):
        return f"{self.brand} {self.model} ({self.state_number})"


class Ownership(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата конца", null=True, blank=True)


class DriverLicense(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE, related_name="licenses")
    number = models.CharField("Номер удостоверения", max_length=10)
    type = models.CharField("Тип", max_length=10)
    issue_date = models.DateField("Дата выдачи")
