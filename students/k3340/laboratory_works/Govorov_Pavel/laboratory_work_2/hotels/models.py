from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Hotel(models.Model):
    name = models.CharField("Название", max_length=150)
    owner = models.CharField("Владелец", max_length=150)
    address = models.CharField("Адрес", max_length=250)
    description = models.TextField("Описание")

    class Meta:
        ordering = ["name", "pk"]
        verbose_name = "отель"
        verbose_name_plural = "отели"

    def __str__(self):
        return self.name


class Room(models.Model):
    class Type(models.TextChoices):
        STANDARD = "standard", "Стандарт"
        SUPERIOR = "superior", "Улучшенный"
        SUITE = "suite", "Люкс"

    hotel = models.ForeignKey(
        Hotel, on_delete=models.CASCADE, related_name="rooms", verbose_name="Отель"
    )
    number = models.CharField("Номер", max_length=10)
    room_type = models.CharField("Тип", max_length=20, choices=Type.choices)
    price = models.DecimalField(
        "Цена за ночь, ₽",
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )
    capacity = models.PositiveSmallIntegerField(
        "Вместимость", validators=[MinValueValidator(1)]
    )
    amenities = models.TextField("Удобства")

    class Meta:
        ordering = ["hotel__name", "number", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["hotel", "number"], name="unique_hotel_room"
            ),
            models.CheckConstraint(
                condition=Q(price__gt=0), name="positive_room_price"
            ),
            models.CheckConstraint(
                condition=Q(capacity__gte=1), name="positive_capacity"
            ),
        ]
        verbose_name = "номер"
        verbose_name_plural = "номера"

    def __str__(self):
        return f"{self.hotel} — №{self.number}"


class Booking(models.Model):
    class Status(models.TextChoices):
        RESERVED = "reserved", "Забронирован"
        CHECKED_IN = "checked_in", "Заселён"
        CHECKED_OUT = "checked_out", "Выселен"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="Постоялец"
    )
    room = models.ForeignKey(Room, on_delete=models.PROTECT, verbose_name="Номер")
    arrival = models.DateField("Дата заезда")
    departure = models.DateField("Дата выезда")
    guests = models.PositiveSmallIntegerField(
        "Количество гостей", default=1, validators=[MinValueValidator(1)]
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.RESERVED
    )
    checked_in_at = models.DateField("Фактическое заселение", blank=True, null=True)
    checked_out_at = models.DateField("Фактическое выселение", blank=True, null=True)

    class Meta:
        ordering = ["-arrival", "-pk"]
        constraints = [
            models.CheckConstraint(
                condition=Q(departure__gt=F("arrival")), name="booking_dates_order"
            ),
            models.CheckConstraint(condition=Q(guests__gte=1), name="positive_guests"),
        ]
        verbose_name = "бронирование"
        verbose_name_plural = "бронирования"

    def clean(self):
        super().clean()
        errors = {}
        if self.arrival and self.departure and self.departure <= self.arrival:
            errors["departure"] = "Выезд должен быть позже заезда."
        if self.room_id and self.guests and self.guests > self.room.capacity:
            errors["guests"] = "Число гостей превышает вместимость номера."
        if self.room_id and self.arrival and self.departure:
            overlaps = Booking.objects.filter(
                room_id=self.room_id,
                arrival__lt=self.departure,
                departure__gt=self.arrival,
            ).exclude(pk=self.pk)
            if overlaps.exists():
                errors["arrival"] = "Номер уже забронирован на эти даты."
        if self.status == self.Status.RESERVED and (
            self.checked_in_at or self.checked_out_at
        ):
            errors["status"] = (
                "У брони до заселения не может быть фактических дат проживания."
            )
        if (
            self.status in [self.Status.CHECKED_IN, self.Status.CHECKED_OUT]
            and not self.checked_in_at
        ):
            errors["checked_in_at"] = "Укажите дату фактического заселения."
        if self.status == self.Status.CHECKED_IN and self.checked_out_at:
            errors["checked_out_at"] = "При выселении выберите статус «Выселен»."
        if self.status == self.Status.CHECKED_OUT and not self.checked_out_at:
            errors["checked_out_at"] = "Укажите дату фактического выселения."
        today = timezone.localdate()
        if self.checked_in_at and self.checked_in_at > today:
            errors["checked_in_at"] = "Фактическое заселение не может быть в будущем."
        if self.checked_out_at and self.checked_out_at > today:
            errors["checked_out_at"] = "Фактическое выселение не может быть в будущем."
        if (
            self.checked_in_at
            and self.checked_out_at
            and self.checked_out_at < self.checked_in_at
        ):
            errors["checked_out_at"] = "Выселение не может быть раньше заселения."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.user} — {self.room} ({self.arrival} – {self.departure})"


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор"
    )
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="reviews", verbose_name="Номер"
    )
    arrival = models.DateField("Начало проживания")
    departure = models.DateField("Конец проживания")
    text = models.TextField("Отзыв")
    rating = models.PositiveSmallIntegerField(
        "Оценка (1–10)", validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    created_at = models.DateTimeField("Дата отзыва", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=1, rating__lte=10), name="review_rating_range"
            ),
            models.CheckConstraint(
                condition=Q(departure__gt=F("arrival")), name="review_dates_order"
            ),
        ]
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"

    def clean(self):
        super().clean()
        if self.arrival and self.departure and self.departure <= self.arrival:
            raise ValidationError(
                {"departure": "Конец проживания должен быть позже начала."}
            )

    def __str__(self):
        return f"{self.user}: {self.rating}/10 — {self.room}"
