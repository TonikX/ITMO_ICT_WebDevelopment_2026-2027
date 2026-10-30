
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    passport_number = models.CharField('Номер паспорта', max_length=30, blank=True)
    home_address = models.CharField('Домашний адрес', max_length=200, blank=True)
    nationality = models.CharField('Национальность', max_length=50, blank=True)

    class Meta:
        verbose_name = 'пользователь (владелец)'
        verbose_name_plural = 'пользователи (владельцы)'

    def __str__(self):
        return f'{self.last_name or self.username} {self.first_name}'.strip()

class Car(models.Model):

    brand = models.CharField('Марка', max_length=30)
    model = models.CharField('Модель', max_length=30)
    color = models.CharField('Цвет', max_length=30)
    state_number = models.CharField('Гос. номер', max_length=10)
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='Ownership', related_name='cars'
    )

    class Meta:
        verbose_name = 'автомобиль'
        verbose_name_plural = 'автомобили'

    def __str__(self):
        return f'{self.brand} {self.model} ({self.state_number})'

class Ownership(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ownerships'
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='ownerships')
    start_date = models.DateField('Дата покупки')
    end_date = models.DateField('Дата продажи', null=True, blank=True)

    class Meta:
        verbose_name = 'владение'
        verbose_name_plural = 'владения'

    def __str__(self):
        end = self.end_date or 'по настоящее время'
        return f'{self.owner} -> {self.car} ({self.start_date} — {end})'
