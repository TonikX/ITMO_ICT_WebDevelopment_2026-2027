from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CarOwner(AbstractUser):
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    passport = models.CharField('Номер паспорта', max_length=10, blank=True)
    address = models.CharField('Домашний адрес', max_length=200, blank=True)
    nationality = models.CharField('Национальность', max_length=50, blank=True)

    class Meta:
        verbose_name = 'автовладелец'
        verbose_name_plural = 'автовладельцы'

    def __str__(self):
        return self.get_full_name() or self.username


class Car(models.Model):
    plate = models.CharField('Госномер', max_length=15)
    brand = models.CharField('Марка', max_length=20)
    model_name = models.CharField('Модель', max_length=20)
    color = models.CharField('Цвет', max_length=30, null=True, blank=True)
    owners = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Ownership', related_name='cars')

    class Meta:
        verbose_name = 'автомобиль'
        verbose_name_plural = 'автомобили'

    def __str__(self):
        return f'{self.brand} {self.model_name} ({self.plate})'


class Ownership(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Автомобиль')
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания', null=True, blank=True)

    class Meta:
        ordering = ['start_date']
        verbose_name = 'владение'
        verbose_name_plural = 'владения'

    def __str__(self):
        return f'{self.owner}: {self.car}'


class DriverLicense(models.Model):
    KINDS = (
        ('A', 'A - мотоциклы'),
        ('B', 'B - легковые'),
        ('C', 'C - грузовые'),
        ('D', 'D - автобусы'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='licenses', verbose_name='Владелец')
    number = models.CharField('Номер удостоверения', max_length=10)
    kind = models.CharField('Тип', max_length=10, choices=KINDS)
    issue_date = models.DateField('Дата выдачи')

    class Meta:
        verbose_name = 'водительское удостоверение'
        verbose_name_plural = 'водительские удостоверения'

    def __str__(self):
        return self.number
