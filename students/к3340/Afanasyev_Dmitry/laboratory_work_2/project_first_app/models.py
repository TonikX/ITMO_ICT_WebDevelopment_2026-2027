from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q, F


class Car(models.Model):
    plate_number = models.CharField('Госномер', max_length=15, unique=True)
    brand = models.CharField('Марка', max_length=20)
    model_name = models.CharField('Модель', max_length=20)
    color = models.CharField('Цвет', max_length=30, blank=True)
    owners = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Ownership', related_name='cars')

    class Meta:
        ordering = ['plate_number']
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

    def __str__(self):
        return f'{self.brand} {self.model_name} · {self.plate_number}'


class Ownership(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Автомобиль')
    start_date = models.DateField('Начало владения')
    end_date = models.DateField('Окончание владения', null=True, blank=True)

    class Meta:
        verbose_name = 'Владение'
        verbose_name_plural = 'Владения'
        constraints = [models.CheckConstraint(condition=Q(end_date__isnull=True) | Q(end_date__gt=F('start_date')), name='ownership_end_after_start')]

    def clean(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'Окончание должно быть позже начала владения.'})
        if self.car_id and self.start_date:
            overlaps = Ownership.objects.filter(car_id=self.car_id).exclude(pk=self.pk)
            if self.end_date:
                overlaps = overlaps.filter(start_date__lt=self.end_date)
            overlaps = overlaps.filter(Q(end_date__isnull=True) | Q(end_date__gt=self.start_date))
            if overlaps.exists():
                raise ValidationError('Периоды владения одним автомобилем не должны пересекаться.')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            Car.objects.select_for_update().get(pk=self.car_id)
            self.full_clean()
            return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.owner} → {self.car}'


class DriverLicense(models.Model):
    class Category(models.TextChoices):
        A = 'A', 'A — мотоциклы'
        B = 'B', 'B — легковые автомобили'
        C = 'C', 'C — грузовые автомобили'
        D = 'D', 'D — автобусы'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='licenses', verbose_name='Владелец')
    number = models.CharField('Номер удостоверения', max_length=10, unique=True)
    category = models.CharField('Категория', max_length=10, choices=Category.choices)
    issued_at = models.DateField('Дата выдачи')

    class Meta:
        verbose_name = 'Водительское удостоверение'
        verbose_name_plural = 'Водительские удостоверения'

    def __str__(self):
        return f'{self.number} ({self.category})'
