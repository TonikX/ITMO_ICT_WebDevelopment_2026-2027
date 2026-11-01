from django.contrib.auth.models import AbstractUser
from django.db import models


class Owner(AbstractUser):
    first_name = models.CharField('Имя', max_length=30)
    last_name = models.CharField('Фамилия', max_length=30)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    passport = models.CharField('Номер паспорта', max_length=20)
    address = models.CharField('Домашний адрес', max_length=200)
    nationality = models.CharField('Национальность', max_length=50)

    def __str__(self):
        return self.get_full_name() or self.username

    class Meta:
        verbose_name = 'Владелец'
        verbose_name_plural = 'Владельцы'


class Car(models.Model):
    plate = models.CharField('Госномер', max_length=15)
    brand = models.CharField('Марка', max_length=20)
    model = models.CharField('Модель', max_length=20)
    color = models.CharField('Цвет', max_length=30, blank=True, null=True)
    owners = models.ManyToManyField(Owner, through='Ownership', related_name='cars')

    def __str__(self):
        return f'{self.brand} {self.model} ({self.plate})'

    class Meta:
        ordering = ['id']
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'


class Ownership(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, verbose_name='Владелец')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Автомобиль')
    start_date = models.DateField('Дата начала владения')
    end_date = models.DateField('Дата окончания владения', null=True, blank=True)

    def __str__(self):
        return f'{self.owner} — {self.car}'

    class Meta:
        verbose_name = 'Владение'
        verbose_name_plural = 'Владения'


class License(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, verbose_name='Владелец')
    number = models.CharField('Номер удостоверения', max_length=10)
    license_type = models.CharField('Тип', max_length=10, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    issued_at = models.DateField('Дата выдачи')

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = 'Водительское удостоверение'
        verbose_name_plural = 'Водительские удостоверения'
