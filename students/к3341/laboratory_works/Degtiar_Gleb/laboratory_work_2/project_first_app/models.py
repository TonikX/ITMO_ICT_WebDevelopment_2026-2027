from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

class Car(models.Model):
    plate = models.CharField('Госномер',max_length=15,unique=True)
    brand = models.CharField('Марка',max_length=20)
    model_name = models.CharField('Модель',max_length=20)
    color = models.CharField('Цвет',max_length=30,blank=True)
    owners = models.ManyToManyField(settings.AUTH_USER_MODEL,through='Ownership',related_name='cars')
    def __str__(self): return f'{self.brand} {self.model_name} · {self.plate}'
    class Meta: ordering=['pk']

class Ownership(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    car = models.ForeignKey(Car,on_delete=models.CASCADE)
    start_date = models.DateField('Начало владения')
    end_date = models.DateField('Окончание владения',null=True,blank=True)
    class Meta:
        constraints=[models.CheckConstraint(check=models.Q(end_date__isnull=True)|models.Q(end_date__gte=models.F('start_date')),name='ownership_dates_valid')]
    def clean(self):
        if not self.start_date: return
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError('Окончание владения раньше начала.')
        if not self.car_id: return
        qs=Ownership.objects.filter(car_id=self.car_id).exclude(pk=self.pk)
        # Границы интервалов включены: продажа и новое владение в разные дни.
        if self.end_date: qs=qs.filter(start_date__lte=self.end_date)
        qs=qs.filter(models.Q(end_date__isnull=True)|models.Q(end_date__gte=self.start_date))
        if qs.exists(): raise ValidationError('Периоды владения этим автомобилем пересекаются.')
    def __str__(self): return f'{self.owner} — {self.car}'

class DrivingLicense(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='licenses')
    number = models.CharField('Номер удостоверения',max_length=10,unique=True)
    category = models.CharField('Тип',max_length=10,choices=[('A','A'),('B','B'),('C','C'),('D','D'),('BE','BE')])
    issued_at = models.DateField('Дата выдачи')
    def __str__(self): return f'{self.number} ({self.category})'
