from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    passport_number = models.CharField(max_length=10, blank=True, verbose_name='Номер паспорта')
    home_address = models.CharField(max_length=200, blank=True, verbose_name='Домашний адрес')
    nationality = models.CharField(max_length=50, blank=True, verbose_name='Национальность')
    cars = models.ManyToManyField(
        'Car',
        through='Ownership',
        related_name='owners',
        verbose_name='Автомобили',
    )

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Car(models.Model):
    WHITE = 'белый'
    BLACK = 'чёрный'
    BLUE = 'синий'
    GREY = 'серый'
    RED = 'красный'
    GREEN = 'зелёный'
    COLOR_CHOICES = [
        (WHITE, 'белый'), (BLACK, 'чёрный'), (BLUE, 'синий'),
        (GREY, 'серый'), (RED, 'красный'), (GREEN, 'зелёный'),
    ]

    plate_number = models.CharField(max_length=15, verbose_name='Гос. номер')
    brand = models.CharField(max_length=20, verbose_name='Марка')
    car_model = models.CharField(max_length=20, verbose_name='Модель')
    color = models.CharField(max_length=30, choices=COLOR_CHOICES, blank=True, verbose_name='Цвет')

    def __str__(self):
        return f'{self.brand} {self.car_model} ({self.plate_number})'


class Ownership(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Автомобиль')
    date_start = models.DateField(verbose_name='Дата начала владения')
    date_end = models.DateField(null=True, blank=True, verbose_name='Дата окончания')

    def __str__(self):
        return f'{self.owner} — {self.car}'


class DriverLicense(models.Model):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    TYPE_CHOICES = [(A, 'мотоцикл'), (B, 'легковой'), (C, 'грузовой'), (D, 'автобус')]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
    )
    number = models.CharField(max_length=10, verbose_name='Номер удостоверения')
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, verbose_name='Тип')
    date_issued = models.DateField(verbose_name='Дата выдачи')

    def __str__(self):
        return f'{self.number} ({self.get_type_display()})'
