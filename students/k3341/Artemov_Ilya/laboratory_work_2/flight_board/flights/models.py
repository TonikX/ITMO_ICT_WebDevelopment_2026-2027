from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import F, Q


class Flight(models.Model):
    class Direction(models.TextChoices):
        ARRIVAL = "arrival", "Прилёт"
        DEPARTURE = "departure", "Отлёт"

    number = models.CharField("Номер рейса", max_length=12)
    airline = models.CharField("Авиакомпания", max_length=100)
    origin = models.CharField("Аэропорт отправления", max_length=100)
    destination = models.CharField("Аэропорт прибытия", max_length=100)
    departure_at = models.DateTimeField("Время отлёта")
    arrival_at = models.DateTimeField("Время прилёта")
    direction = models.CharField("Тип", max_length=9, choices=Direction.choices)
    gate = models.CharField("Номер гейта", max_length=10)
    seat_count = models.PositiveIntegerField("Количество мест", validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["departure_at", "pk"]
        verbose_name = "рейс"
        verbose_name_plural = "рейсы"
        constraints = [
            models.UniqueConstraint(fields=["number", "departure_at"], name="unique_flight_departure"),
            models.CheckConstraint(condition=Q(arrival_at__gt=F("departure_at")), name="flight_times_order"),
            models.CheckConstraint(condition=Q(seat_count__gte=1), name="flight_positive_seats"),
            models.CheckConstraint(condition=Q(direction__in=["arrival", "departure"]), name="flight_direction_valid"),
        ]

    def clean(self):
        super().clean()
        if self.arrival_at and self.departure_at and self.arrival_at <= self.departure_at:
            raise ValidationError({"arrival_at": "Прилёт должен быть позже отлёта."})
        if self.pk and self.seat_count is not None:
            if self.reservations.filter(seat_number__gt=self.seat_count).exists():
                raise ValidationError({"seat_count": "На удаляемые места уже есть бронирования."})

    def __str__(self):
        return f"{self.number}: {self.origin} → {self.destination}"


class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="reservations", verbose_name="Пользователь")
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE,
                               related_name="reservations", verbose_name="Рейс")
    passenger_name = models.CharField("ФИО пассажира", max_length=150)
    seat_number = models.PositiveIntegerField("Номер места", validators=[MinValueValidator(1)])
    ticket_number = models.CharField("Номер билета", max_length=30, unique=True, null=True, blank=True)
    checked_in = models.BooleanField("Зарегистрирован на рейс", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        ordering = ["flight_id", "seat_number"]
        verbose_name = "бронирование"
        verbose_name_plural = "бронирования"
        constraints = [
            models.UniqueConstraint(fields=["flight", "seat_number"], name="unique_flight_seat"),
            models.CheckConstraint(condition=Q(seat_number__gte=1), name="reservation_positive_seat"),
            models.CheckConstraint(
                condition=Q(checked_in=False) | (Q(ticket_number__isnull=False) & ~Q(ticket_number="")),
                name="checkin_requires_ticket",
            ),
        ]

    def clean(self):
        super().clean()
        self.ticket_number = self.ticket_number.strip() if self.ticket_number else None
        if self.checked_in and not self.ticket_number:
            raise ValidationError({"ticket_number": "Для регистрации нужен номер билета."})
        if self.flight_id and self.seat_number:
            if self.seat_number > self.flight.seat_count:
                raise ValidationError({"seat_number": f"Укажите место от 1 до {self.flight.seat_count}."})
            if Reservation.objects.filter(flight_id=self.flight_id, seat_number=self.seat_number).exclude(pk=self.pk).exists():
                raise ValidationError({"seat_number": "Это место уже занято."})

    def __str__(self):
        return f"{self.flight.number}, место {self.seat_number} — {self.passenger_name}"


class Review(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="reviews", verbose_name="Рейс")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="flight_reviews", verbose_name="Комментатор")
    flight_date = models.DateField("Дата рейса")
    text = models.TextField("Текст отзыва")
    rating = models.PositiveSmallIntegerField("Рейтинг", validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"
        constraints = [models.CheckConstraint(condition=Q(rating__gte=1, rating__lte=10), name="review_rating_1_10")]

    def __str__(self):
        return f"{self.user} о {self.flight.number}: {self.rating}/10"
