"""
Модель данных об автовладельцах (практики 2.1–2.3).

Практика 2.3: «Владелец автомобиля» сделан пользователем — модель CarOwner
унаследована от AbstractUser и подключена в settings.py через AUTH_USER_MODEL.
Поля first_name и last_name уже есть в AbstractUser.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class CarOwner(AbstractUser):
    """Автовладелец (пользователь системы)"""
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    # Поля из практики 2.3
    passport_number = models.CharField('Номер паспорта', max_length=20, blank=True)
    home_address = models.CharField('Домашний адрес', max_length=255, blank=True)
    nationality = models.CharField('Национальность', max_length=50, blank=True)

    class Meta:
        verbose_name = 'Автовладелец'
        verbose_name_plural = 'Автовладельцы'

    def __str__(self):
        full_name = f'{self.last_name} {self.first_name}'.strip()
        return full_name or self.username


class Car(models.Model):
    """Автомобиль"""
    license_plate = models.CharField('Гос. номер', max_length=15, unique=True)
    brand = models.CharField('Марка', max_length=20)
    model = models.CharField('Модель', max_length=20)
    color = models.CharField('Цвет', max_length=30, null=True, blank=True)
    # M:N с владельцами через ассоциативную сущность Ownership (практика 2.2)
    owners = models.ManyToManyField(CarOwner, through='Ownership',
                                    related_name='cars', verbose_name='Владельцы')

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

    def __str__(self):
        return f'{self.brand} {self.model} ({self.license_plate})'


class Ownership(models.Model):
    """Владение: ассоциативная сущность между владельцем и автомобилем"""
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE,
                              related_name='ownerships', verbose_name='Владелец')
    car = models.ForeignKey(Car, on_delete=models.CASCADE,
                            related_name='ownerships', verbose_name='Автомобиль')
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата конца', null=True, blank=True)

    class Meta:
        verbose_name = 'Владение'
        verbose_name_plural = 'Владения'

    def __str__(self):
        return f'{self.owner} — {self.car}: {self.start_date} … {self.end_date or "н.в."}'


class DriverLicense(models.Model):
    """Водительское удостоверение"""
    TYPES = (
        ('A', 'A — мотоциклы'),
        ('B', 'B — легковые автомобили'),
        ('C', 'C — грузовые автомобили'),
        ('D', 'D — автобусы'),
    )
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE,
                              related_name='licenses', verbose_name='Владелец')
    number = models.CharField('Номер удостоверения', max_length=10, unique=True)
    type = models.CharField('Тип', max_length=1, choices=TYPES)
    issue_date = models.DateField('Дата выдачи')

    class Meta:
        verbose_name = 'Водительское удостоверение'
        verbose_name_plural = 'Водительские удостоверения'

    def __str__(self):
        return f'{self.number} ({self.get_type_display()})'
