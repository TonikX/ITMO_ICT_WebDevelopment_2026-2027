from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    passport_number = models.CharField('Номер паспорта', max_length=20, blank=True)
    home_address = models.CharField('Домашний адрес', max_length=255, blank=True)
    nationality = models.CharField('Национальность', max_length=50, blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        full = f'{self.last_name} {self.first_name}'.strip()
        return full or self.username


class DriverLicense(models.Model):
    CATEGORY_CHOICES = [
        ('A', 'A — мотоциклы'),
        ('B', 'B — легковые'),
        ('C', 'C — грузовые'),
        ('D', 'D — автобусы'),
        ('BE', 'BE — легковые с прицепом'),
        ('CE', 'CE — грузовые с прицепом'),
        ('DE', 'DE — автобусы с прицепом'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='licenses',
        verbose_name='Владелец'
    )
    license_number = models.CharField('Номер удостоверения', max_length=10)
    category = models.CharField(
        'Категория', max_length=3,
        choices=CATEGORY_CHOICES, default='B'
    )
    issued_date = models.DateField('Дата выдачи', null=True, blank=True)

    class Meta:
        verbose_name = 'Водительское удостоверение'
        verbose_name_plural = 'Водительские удостоверения'
        ordering = ['owner', 'license_number']

    def __str__(self):
        return f'{self.license_number} ({self.get_category_display()})'


class Car(models.Model):
    COLOR_CHOICES = [
        ('white', 'Белый'),
        ('black', 'Чёрный'),
        ('silver', 'Серебристый'),
        ('gray', 'Серый'),
        ('red', 'Красный'),
        ('blue', 'Синий'),
        ('green', 'Зелёный'),
        ('other', 'Другой'),
    ]

    state_number = models.CharField('Гос. номер', max_length=15, unique=True)
    brand = models.CharField('Марка', max_length=20)
    model = models.CharField('Модель', max_length=20)
    color = models.CharField(
        'Цвет', max_length=10,
        choices=COLOR_CHOICES, default='white', blank=True
    )

    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Ownership',
        related_name='cars',
        verbose_name='Владельцы'
    )

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'
        ordering = ['brand', 'model']

    def __str__(self):
        return f'{self.brand} {self.model} ({self.state_number})'


class Ownership(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='ownerships', verbose_name='Владелец'
    )
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE,
        related_name='ownerships', verbose_name='Автомобиль'
    )
    start_date = models.DateField('Дата начала владения')
    end_date = models.DateField('Дата окончания владения', null=True, blank=True)

    class Meta:
        verbose_name = 'Владение'
        verbose_name_plural = 'Владения'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.owner} → {self.car}'