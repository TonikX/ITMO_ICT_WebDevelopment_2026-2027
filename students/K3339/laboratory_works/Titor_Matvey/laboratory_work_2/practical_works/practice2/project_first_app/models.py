
from django.db import models

class Owner(models.Model):

    first_name = models.CharField('Имя', max_length=30)
    last_name = models.CharField('Фамилия', max_length=30)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'владелец'
        verbose_name_plural = 'владельцы'

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

class Car(models.Model):

    brand = models.CharField('Марка', max_length=30)
    model = models.CharField('Модель', max_length=30)
    color = models.CharField('Цвет', max_length=30)
    state_number = models.CharField('Гос. номер', max_length=10)
    owners = models.ManyToManyField(Owner, through='Ownership', related_name='cars')

    class Meta:
        verbose_name = 'автомобиль'
        verbose_name_plural = 'автомобили'

    def __str__(self):
        return f'{self.brand} {self.model} ({self.state_number})'

class Ownership(models.Model):

    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='ownerships')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='ownerships')
    start_date = models.DateField('Дата покупки')
    end_date = models.DateField('Дата продажи', null=True, blank=True)

    class Meta:
        verbose_name = 'владение'
        verbose_name_plural = 'владения'

    def __str__(self):
        end = self.end_date or 'по настоящее время'
        return f'{self.owner} -> {self.car} ({self.start_date} — {end})'
