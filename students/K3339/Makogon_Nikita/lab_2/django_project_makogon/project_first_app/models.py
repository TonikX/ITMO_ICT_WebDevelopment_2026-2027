from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# расширяем AbstractUser
class CarOwner(AbstractUser):
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    passport_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер паспорта")
    home_address = models.CharField(max_length=150, blank=True, null=True, verbose_name="Домашний адрес")
    nationality = models.CharField(max_length=50, blank=True, null=True, verbose_name="Национальность")

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"

class Car(models.Model):
    state_number = models.CharField(max_length=15, verbose_name="Гос. номер")
    brand = models.CharField(max_length=20, verbose_name="Марка")
    model_name = models.CharField(max_length=20, verbose_name="Модель")
    color = models.CharField(max_length=30, null=True, blank=True, verbose_name="Цвет")

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.state_number})"

class Ownership(models.Model):
    # ссылаемся на AUTH_USER_MODEL
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата окончания")

    def __str__(self):
        return f"{self.owner} — {self.car}"

class DriverLicense(models.Model):
    LICENSE_TYPES = (
        ('A', 'Категория A'),
        ('B', 'Категория B'),
        ('C', 'Категория C'),
        ('D', 'Категория D'),
    )
    # ссылаемся на AUTH_USER_MODEL
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец")
    license_number = models.CharField(max_length=10, verbose_name="Номер удостоверения")
    type = models.CharField(max_length=10, choices=LICENSE_TYPES, verbose_name="Тип")
    issue_date = models.DateField(verbose_name="Дата выдачи")