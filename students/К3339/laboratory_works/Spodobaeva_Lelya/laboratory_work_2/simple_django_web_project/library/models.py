from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Tour(models.Model):
    name = models.CharField("Название тура", max_length=150)
    agency = models.CharField("Турагентство", max_length=150)
    country = models.CharField("Страна", max_length=100)
    description = models.TextField("Описание тура")
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")
    payment_terms = models.TextField("Условия оплаты")
    price = models.DecimalField(
        "Стоимость",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        ordering = ["start_date", "name"]
        verbose_name = "Тур"
        verbose_name_plural = "Туры"
        constraints = [
            models.CheckConstraint(check=models.Q(price__gt=0), name="tour_positive_price"),
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F("start_date")),
                name="tour_valid_date_range",
            ),
        ]

    def clean(self):
        super().clean()
        if (
            isinstance(self.start_date, date)
            and isinstance(self.end_date, date)
            and self.end_date < self.start_date
        ):
            raise ValidationError({"end_date": "Дата окончания не может быть раньше даты начала."})

    def __str__(self):
        return f"{self.name} ({self.country})"


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
    tourists_count = models.PositiveIntegerField(
        "Количество туристов",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(2_147_483_647)],
    )
    comment = models.TextField("Комментарий", blank=True)
    is_confirmed = models.BooleanField("Подтверждено администратором", default=False)
    created_at = models.DateTimeField("Дата бронирования", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        constraints = [
            models.CheckConstraint(
                check=models.Q(tourists_count__gte=1), name="reservation_positive_tourists"
            ),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.tour.name}"


class Review(models.Model):
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Тур",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Комментатор",
    )
    tour_start_date = models.DateField("Дата начала тура")
    tour_end_date = models.DateField("Дата окончания тура")
    text = models.TextField("Текст комментария")
    rating = models.PositiveSmallIntegerField(
        "Рейтинг",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    created_at = models.DateTimeField("Дата комментария", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__range=(1, 10)), name="review_rating_range"
            ),
        ]

    def __str__(self):
        return f"{self.tour.name}: {self.rating}/10"
