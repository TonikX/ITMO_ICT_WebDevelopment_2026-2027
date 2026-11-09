from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Car(models.Model):
    registration_number = models.CharField('Государственный номер', max_length=15, unique=True)
    brand = models.CharField('Марка', max_length=20)
    model = models.CharField('Модель', max_length=20)
    color = models.CharField('Цвет', max_length=30, blank=True)
    owners = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Ownership', related_name='cars', verbose_name='Владельцы')

    class Meta:
        verbose_name = 'автомобиль'
        verbose_name_plural = 'автомобили'
        ordering = ['registration_number']

    def __str__(self):
        return f'{self.brand} {self.model} · {self.registration_number}'


class Ownership(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Автомобиль')
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания', null=True, blank=True)

    class Meta:
        verbose_name = 'владение'
        verbose_name_plural = 'владения'

    def __str__(self):
        return f'{self.owner} · {self.car}'

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'Окончание владения не может быть раньше начала.'})


class DriverLicense(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец')
    number = models.CharField('Номер удостоверения', max_length=10)
    category = models.CharField('Категория', max_length=10)
    issued_at = models.DateField('Дата выдачи')

    class Meta:
        verbose_name = 'водительское удостоверение'
        verbose_name_plural = 'водительские удостоверения'

    def __str__(self):
        return f'{self.number} · {self.category}'
