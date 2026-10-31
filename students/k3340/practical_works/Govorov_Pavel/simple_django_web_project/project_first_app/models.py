from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class Owner(AbstractUser):
    first_name = models.CharField("Имя", max_length=30)
    last_name = models.CharField("Фамилия", max_length=30)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    passport_number = models.CharField("Номер паспорта", max_length=20, blank=True)
    home_address = models.CharField("Домашний адрес", max_length=250, blank=True)
    nationality = models.CharField("Национальность", max_length=80, blank=True)

    class Meta:
        ordering = ["last_name", "first_name", "pk"]
        verbose_name = "владелец"
        verbose_name_plural = "владельцы"

    def __str__(self):
        return self.get_full_name() or self.username


class Car(models.Model):
    plate = models.CharField("Госномер", max_length=15, unique=True)
    brand = models.CharField("Марка", max_length=20)
    model = models.CharField("Модель", max_length=20)
    color = models.CharField("Цвет", max_length=30, blank=True)
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Ownership", related_name="cars"
    )

    class Meta:
        ordering = ["plate"]
        verbose_name = "автомобиль"
        verbose_name_plural = "автомобили"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate})"


class Ownership(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")
    start_date = models.DateField("Начало владения")
    end_date = models.DateField("Окончание владения", null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__isnull=True) | Q(end_date__gt=F("start_date")),
                name="ownership_dates_order",
            )
        ]
        verbose_name = "владение"
        verbose_name_plural = "владения"

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError("Окончание владения должно быть позже начала.")
        if self.car_id and self.start_date:
            others = Ownership.objects.filter(car_id=self.car_id).exclude(pk=self.pk)
            if self.end_date:
                others = others.filter(start_date__lt=self.end_date)
            if others.filter(
                Q(end_date__isnull=True) | Q(end_date__gt=self.start_date)
            ).exists():
                raise ValidationError("Периоды владения этим автомобилем пересекаются.")

    def __str__(self):
        return f"{self.owner} — {self.car}"


class DrivingLicense(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )
    number = models.CharField("Номер удостоверения", max_length=10, unique=True)
    license_type = models.CharField("Тип", max_length=10)
    issued_at = models.DateField("Дата выдачи")

    class Meta:
        verbose_name = "водительское удостоверение"
        verbose_name_plural = "водительские удостоверения"

    def __str__(self):
        return self.number
