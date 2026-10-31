from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Country(models.Model):
    name = models.CharField("Название", max_length=100)

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"
        ordering = ["name"]

    def __str__(self):
        return self.name


class TravelAgency(models.Model):
    name = models.CharField("Название", max_length=150)

    class Meta:
        verbose_name = "Турагентство"
        verbose_name_plural = "Турагентства"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tour(models.Model):
    name = models.CharField("Название тура", max_length=150)
    agency = models.ForeignKey(
        TravelAgency,
        on_delete=models.CASCADE,
        related_name="tours",
        verbose_name="Турагентство",
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="tours",
        verbose_name="Страна",
    )
    description = models.TextField("Описание")
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")
    payment_terms = models.TextField("Условия оплаты")

    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"
        ordering = ["start_date"]

    def __str__(self):
        return self.name


class Reservation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="Пользователь",
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="Тур",
    )
    is_confirmed = models.BooleanField("Подтверждено", default=False)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return f"{self.user} — {self.tour}"


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор",
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Тур",
    )
    start_date = models.DateField("Дата начала тура")
    end_date = models.DateField("Дата окончания тура")
    text = models.TextField("Текст отзыва")
    rating = models.IntegerField(
        "Оценка",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Отзыв {self.user} о туре {self.tour}"
