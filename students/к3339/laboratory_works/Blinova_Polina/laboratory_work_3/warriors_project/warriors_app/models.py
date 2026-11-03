from django.db import models


class CarOwner(models.Model):
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    birth_date = models.DateTimeField(null=True, verbose_name='Дата рождения')

    class Meta:
        verbose_name = 'Автовладелец'
        verbose_name_plural = 'Автовладельцы'

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Car(models.Model):
    state_number = models.CharField(max_length=15, verbose_name='Гос_номер')
    brand = models.CharField(max_length=20, verbose_name='Марка')
    model = models.CharField(max_length=20, verbose_name='Модель')
    color = models.CharField(max_length=30, null=True, verbose_name='Цвет')

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

    def __str__(self):
        return f'{self.brand} {self.model} ({self.state_number})'


class Ownership(models.Model):
    owner = models.ForeignKey(
        CarOwner, on_delete=models.CASCADE, 
        related_name='ownerships', verbose_name='Id_владельца'
    )
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE, 
        related_name='ownerships', verbose_name='Id_автомобиля'
    )
    start_date = models.DateTimeField(verbose_name='Дата_начала')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата_окончания')

    class Meta:
        verbose_name = 'Владение'
        verbose_name_plural = 'Владения'

    def __str__(self):
        return f'{self.owner} - {self.car}'


class DriverLicense(models.Model):
    owner = models.ForeignKey(
        CarOwner, on_delete=models.CASCADE, 
        related_name='licenses', verbose_name='Id_владельца'
    )
    license_number = models.CharField(max_length=10, verbose_name='Номер_удостоверения')
    license_type = models.CharField(max_length=10, verbose_name='Тип')
    issue_date = models.DateTimeField(verbose_name='Дата_выдачи')

    class Meta:
        verbose_name = 'Водительское удостоверение'
        verbose_name_plural = 'Водительские удостоверения'

    def __str__(self):
        return f'{self.license_number} ({self.owner})'