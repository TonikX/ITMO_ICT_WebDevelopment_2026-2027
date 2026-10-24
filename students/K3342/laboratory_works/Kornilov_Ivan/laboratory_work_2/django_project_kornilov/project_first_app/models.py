from django.contrib.auth.models import AbstractUser
from django.db import models


class CarOwner(AbstractUser):
    first_name = models.CharField('Имя', max_length=30)
    last_name = models.CharField('Фамилия', max_length=30)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    passport_number = models.CharField('Номер паспорта', max_length=20, blank=True)
    address = models.CharField('Домашний адрес', max_length=200, blank=True)
    nationality = models.CharField('Национальность', max_length=50, blank=True)

    class Meta:
        verbose_name = 'Автовладелец'
        verbose_name_plural = 'Автовладельцы'

    def __str__(self):
        full_name = f'{self.last_name} {self.first_name}'.strip()
        return full_name or self.username


class Car(models.Model):
    license_plate = models.CharField('Гос. номер', max_length=15)
    brand = models.CharField('Марка', max_length=20)
    model_name = models.CharField('Модель', max_length=20)
    color = models.CharField('Цвет', max_length=30, null=True, blank=True)
    owners = models.ManyToManyField(
        CarOwner,
        through='Ownership',
        related_name='cars',
        verbose_name='Владельцы',
    )

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

    def __str__(self):
        return f'{self.brand} {self.model_name} ({self.license_plate})'


class Ownership(models.Model):
    owner = models.ForeignKey(
        CarOwner,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ownerships',
        verbose_name='Владелец',
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ownerships',
        verbose_name='Автомобиль',
    )
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания', null=True, blank=True)

    class Meta:
        verbose_name = 'Владение'
        verbose_name_plural = 'Владения'
        ordering = ['start_date']

    def __str__(self):
        return f'{self.owner} — {self.car}'


class DrivingLicense(models.Model):
    LICENSE_TYPES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('BE', 'BE'),
        ('CE', 'CE'),
    ]

    owner = models.ForeignKey(
        CarOwner,
        on_delete=models.CASCADE,
        related_name='licenses',
        verbose_name='Владелец',
    )
    license_number = models.CharField('Номер удостоверения', max_length=10)
    license_type = models.CharField('Тип', max_length=10, choices=LICENSE_TYPES, null=True, blank=True)
    issue_date = models.DateField('Дата выдачи')

    class Meta:
        verbose_name = 'Водительское удостоверение'
        verbose_name_plural = 'Водительские удостоверения'

    def __str__(self):
        return f'{self.license_number} ({self.license_type})'
