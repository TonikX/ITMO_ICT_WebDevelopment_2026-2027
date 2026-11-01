from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class CarOwner(AbstractUser):
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    passport_number = models.CharField("Номер паспорта", max_length=20)
    home_address = models.CharField("Домашний адрес", max_length=200)
    nationality = models.CharField("Национальность", max_length=50)

    class Meta:
        ordering = ["last_name", "first_name", "pk"]
        verbose_name = "Автовладелец"
        verbose_name_plural = "Автовладельцы"

    def __str__(self):
        return self.get_full_name() or self.username


class Car(models.Model):
    plate_number = models.CharField("Государственный номер", max_length=15, unique=True)
    brand = models.CharField("Марка", max_length=20)
    model_name = models.CharField("Модель", max_length=20)
    color = models.CharField("Цвет", max_length=30, blank=True)
    owners = models.ManyToManyField(CarOwner, through="Ownership", related_name="cars")

    class Meta:
        ordering = ["brand", "model_name", "pk"]
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.plate_number})"


class Ownership(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE, verbose_name="Владелец")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")
    start_date = models.DateField("Начало владения")
    end_date = models.DateField("Окончание владения", null=True, blank=True)

    class Meta:
        ordering = ["car", "start_date"]
        verbose_name = "Владение"
        verbose_name_plural = "История владения"

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError("Окончание владения не может быть раньше начала.")
        if self.car_id and self.start_date:
            periods = Ownership.objects.filter(car_id=self.car_id).exclude(pk=self.pk)
            periods = periods.filter(Q(end_date__isnull=True) | Q(end_date__gte=self.start_date))
            if self.end_date:
                periods = periods.filter(start_date__lte=self.end_date)
            if periods.exists():
                raise ValidationError("У автомобиля уже есть владелец в этот период.")

    def __str__(self):
        return f"{self.owner} — {self.car}"


class DrivingLicense(models.Model):
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE, related_name="licenses", verbose_name="Владелец")
    number = models.CharField("Номер удостоверения", max_length=10, unique=True)
    category = models.CharField("Категория", max_length=10)
    issue_date = models.DateField("Дата выдачи")

    class Meta:
        verbose_name = "Водительское удостоверение"
        verbose_name_plural = "Водительские удостоверения"

    def __str__(self):
        return f"{self.number} — {self.owner}"
