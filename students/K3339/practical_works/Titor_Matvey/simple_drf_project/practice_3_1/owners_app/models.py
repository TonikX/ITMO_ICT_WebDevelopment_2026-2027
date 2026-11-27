from django.db import models

class Owner(models.Model):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    birth_date = models.DateField('Дата рождения')
    passport = models.CharField('Паспорт', max_length=30, unique=True)
    address = models.CharField('Адрес', max_length=200, blank=True)
    nationality = models.CharField('Национальность', max_length=50, blank=True)

    class Meta:
        ordering = ['last_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

class Car(models.Model):
    brand = models.CharField('Марка', max_length=50)
    model = models.CharField('Модель', max_length=50)
    color = models.CharField('Цвет', max_length=30)
    state_number = models.CharField('Госномер', max_length=15, unique=True)
    owners = models.ManyToManyField(
        Owner, through='Possession', related_name='cars', verbose_name='Владельцы',
    )

    class Meta:
        ordering = ['brand', 'model']

    def __str__(self):
        return f'{self.brand} {self.model} ({self.state_number})'

class License(models.Model):
    owner = models.OneToOneField(
        Owner, on_delete=models.CASCADE, related_name='license', verbose_name='Владелец',
    )
    number = models.CharField('Номер удостоверения', max_length=30, unique=True)
    license_type = models.CharField('Тип', max_length=10, default='B')
    issued_at = models.DateField('Дата выдачи')

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f'{self.number} ({self.owner})'

class Possession(models.Model):
    owner = models.ForeignKey(
        Owner, on_delete=models.CASCADE, related_name='possessions', verbose_name='Владелец',
    )
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE, related_name='possessions', verbose_name='Автомобиль',
    )
    started_at = models.DateField('Дата начала владения')
    ended_at = models.DateField('Дата окончания владения', null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'car', 'started_at'], name='unique_possession_start',
            ),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.owner} — {self.car} с {self.started_at}'
