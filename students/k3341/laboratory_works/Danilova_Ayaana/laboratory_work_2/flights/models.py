from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Now
from django.urls import reverse

from uuid6 import uuid7 as generate_uuid

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class UUIDModel(models.Model):
    """Абстрактная базовая модель с первичным ключом UUIDv7."""
    id = models.UUIDField(
        primary_key=True,
        default=generate_uuid,
        editable=False,
    )

    if TYPE_CHECKING:
        id: uuid.UUID

    class Meta:
        abstract = True


class User(UUIDModel, AbstractUser):
    email = models.EmailField("Email", unique=True)
    phone_number = models.CharField("Phone number", max_length=15, blank=True)

    if TYPE_CHECKING:
        passengers: RelatedManager[Passenger]
        reservations: RelatedManager[Reservation]
        reviews: RelatedManager[Review]

    class Meta(AbstractUser.Meta):
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"


class Passenger(UUIDModel):
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="passengers",
        verbose_name="Владелец профиля",
    )
    first_name = models.CharField("Имя", max_length=50)
    last_name = models.CharField("Фамилия", max_length=50)
    birth_date = models.DateField("Дата рождения")

    if TYPE_CHECKING:
        owner_id: uuid.UUID
        passports: RelatedManager[Passport]
        tickets: RelatedManager[Ticket]

    class Meta:
        verbose_name = "Пассажир"
        verbose_name_plural = "Пассажиры"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.birth_date.strftime('%d.%m.%Y')})"

    @property
    def active_passport(self) -> Passport | None:
        return self.passports.filter(is_active=True).first()


class Passport(UUIDModel):
    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.PROTECT,
        related_name="passports",
        verbose_name="Пассажир",
    )
    passport_number = models.CharField("Номер паспорта", max_length=20, unique=True)
    is_active = models.BooleanField("Актуальный паспорт", db_default=True)

    if TYPE_CHECKING:
        passenger_id: uuid.UUID

    class Meta:
        verbose_name = "Паспорт"
        verbose_name_plural = "Паспорта"
        indexes = [
            models.Index(
                fields=["passenger"],
                condition=Q(is_active=True),
                name="passenger_active_passport_idx",
            ),
        ]

    def __str__(self) -> str:
        status: str = "Активен" if self.is_active else "Архив"
        return f"{self.passport_number} ({status})"


class FlightType(models.TextChoices):
    DEPARTURE = "DEP", "Отлёт"
    ARRIVAL = "ARR", "Прилёт"


class Flight(UUIDModel):
    flight_number = models.CharField("Номер рейса", max_length=20, unique=True)
    airline = models.CharField("Авиакомпания", max_length=100)
    departure = models.DateTimeField("Время отлета")
    arrival = models.DateTimeField("Время прилета")
    flight_type = models.CharField("Тип", max_length=3, choices=FlightType.choices)
    gate = models.CharField("Гейт", max_length=10)
    capacity = models.PositiveIntegerField("Вместимость борта", db_default=150)

    if TYPE_CHECKING:
        reservations: RelatedManager[Reservation]
        tickets: RelatedManager[Ticket]
        reviews: RelatedManager[Review]

    class Meta:
        verbose_name = "Рейс"
        verbose_name_plural = "Рейсы"
        ordering = ["-departure"]
        indexes = [
            models.Index(
                fields=["flight_type", "-departure"],
                name="flight_type_depart_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(departure__lt=F("arrival")),
                name="flight_time_order_valid",
            ),
            models.CheckConstraint(
                condition=Q(capacity__gte=1),
                name="flight_capacity_positive",
            ),
            models.CheckConstraint(
                condition=Q(flight_type__in=FlightType.values),
                name="flight_type_valid",
            ),
        ]

    def __str__(self) -> str:
        dep_str: str = self.departure.strftime("%d.%m.%Y %H:%M")
        arr_str: str = self.arrival.strftime("%d.%m.%Y %H:%M")
        return f"{self.flight_number} - {self.airline} ({dep_str} - {arr_str})"

    def get_absolute_url(self) -> str:
        return reverse("flights:flight_detail", kwargs={"pk": self.pk})


class Reservation(UUIDModel):
    purchaser = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="reservations",
        verbose_name="Покупатель",
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.PROTECT,
        related_name="reservations",
        verbose_name="Рейс",
    )
    created_at = models.DateTimeField("Дата создания", db_default=Now())

    if TYPE_CHECKING:
        purchaser_id: uuid.UUID
        flight_id: uuid.UUID
        tickets: RelatedManager[Ticket]

    class Meta:
        verbose_name = "Резервирование"
        verbose_name_plural = "Резервирования"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["purchaser", "-created_at"],
                name="res_purchaser_created_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"Бронь #{self.id} (Рейс {self.flight_id})"


class Ticket(UUIDModel):
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name="Резервирование",
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name="Рейс",
    )
    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name="Пассажир",
    )
    seat_number = models.PositiveIntegerField(
        "Номер места",
        validators=[MinValueValidator(1), MaxValueValidator(150)],
    )
    ticket_number = models.CharField(
        "Номер билета",
        max_length=30,
        blank=True,
        default="",
        help_text="Заполняется сотрудником при регистрации на рейс",
    )
    is_checked_in = models.BooleanField("Зарегистрирован на рейс", db_default=False)

    if TYPE_CHECKING:
        reservation_id: uuid.UUID
        flight_id: uuid.UUID
        passenger_id: uuid.UUID

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"
        constraints = [
            models.CheckConstraint(
                condition=Q(seat_number__gte=1, seat_number__lte=150),
                name="ticket_seat_in_range",
            ),
            models.UniqueConstraint(
                fields=["flight", "passenger"],
                name="ticket_flight_passenger_uniq",
            ),
            models.UniqueConstraint(
                fields=["flight", "seat_number"],
                name="ticket_flight_seat_uniq",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.flight_id and self.seat_number:
            if self.seat_number > self.flight.capacity:
                raise ValidationError({
                    "seat_number": f"Номер места не может превышать вместимость борта ({self.flight.capacity})."
                })

    def __str__(self) -> str:
        return f"Билет #{self.pk} (Рейс {self.flight_id}, пассажир {self.passenger_id}, место {self.seat_number})"


class Review(UUIDModel):
    flight = models.ForeignKey(
        Flight,
        on_delete=models.PROTECT,
        related_name="reviews",
        verbose_name="Рейс",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="reviews",
        verbose_name="Пользователь",
    )
    rating = models.PositiveIntegerField(
        "Оценка",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    text = models.TextField("Комментарий", blank=True)
    flight_date = models.DateField("Дата рейса", blank=True, null=True)
    created_at = models.DateTimeField("Дата создания", db_default=Now())

    if TYPE_CHECKING:
        flight_id: uuid.UUID
        author_id: uuid.UUID

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["flight", "-created_at"],
                name="review_flight_created_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=1, rating__lte=10),
                name="review_rating_in_range",
            ),
        ]

    def __str__(self) -> str:
        return f"Отзыв #{self.pk} (Рейс {self.flight_id}, пользователь {self.author_id}, оценка {self.rating})"