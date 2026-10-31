from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class CarOwner(AbstractUser):
    first_name = models.CharField("Имя", max_length=30)
    last_name = models.CharField("Фамилия", max_length=30)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    passport_number = models.CharField("Номер паспорта", max_length=20)
    home_address = models.CharField("Домашний адрес", max_length=255)
    nationality = models.CharField("Национальность", max_length=50)

    class Meta:
        verbose_name = "владелец автомобиля"
        verbose_name_plural = "владельцы автомобилей"
        ordering = ["last_name", "first_name", "pk"]

    def __str__(self):
        return self.get_full_name() or self.username


class Car(models.Model):
    registration_number = models.CharField("Госномер", max_length=15, unique=True)
    brand = models.CharField("Марка", max_length=20)
    model_name = models.CharField("Модель", max_length=20)
    color = models.CharField("Цвет", max_length=30, blank=True, null=True)
    owners = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Ownership",
                                   related_name="cars", verbose_name="Владельцы")

    class Meta:
        ordering = ["registration_number"]
        verbose_name = "автомобиль"
        verbose_name_plural = "автомобили"

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.registration_number})"


class Ownership(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="ownerships", verbose_name="Владелец")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="ownerships",
                            verbose_name="Автомобиль")
    start_date = models.DateField("Дата начала владения")
    end_date = models.DateField("Дата окончания владения", null=True, blank=True)

    class Meta:
        ordering = ["car_id", "start_date"]
        verbose_name = "владение"
        verbose_name_plural = "владения"
        constraints = [models.CheckConstraint(
            condition=Q(end_date__isnull=True) | Q(end_date__gte=F("start_date")),
            name="ownership_dates_order",
        )]

    def clean(self):
        super().clean()
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "Окончание не может быть раньше начала."})
        if self.car_id and self.start_date:
            overlapping = Ownership.objects.filter(car_id=self.car_id).exclude(pk=self.pk)
            overlapping = overlapping.filter(Q(end_date__isnull=True) |
                                              Q(end_date__gte=self.start_date))
            if self.end_date:
                overlapping = overlapping.filter(start_date__lte=self.end_date)
            if overlapping.exists():
                raise ValidationError("Периоды владения одним автомобилем не должны пересекаться.")

    def __str__(self):
        return f"{self.owner} — {self.car} с {self.start_date}"


class DriverLicense(models.Model):
    class Category(models.TextChoices):
        A = "A", "A"
        B = "B", "B"
        C = "C", "C"
        D = "D", "D"
        BE = "BE", "BE"
        CE = "CE", "CE"
        DE = "DE", "DE"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="driver_licenses", verbose_name="Владелец")
    number = models.CharField("Номер удостоверения", max_length=10, unique=True)
    category = models.CharField("Тип", max_length=10, choices=Category.choices)
    issue_date = models.DateField("Дата выдачи")

    class Meta:
        verbose_name = "водительское удостоверение"
        verbose_name_plural = "водительские удостоверения"

    def __str__(self):
        return f"{self.number} ({self.category})"
