from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    passport_number = models.CharField('Номер паспорта', max_length=20, blank=True)
    home_address = models.CharField('Домашний адрес', max_length=255, blank=True)
    nationality = models.CharField('Национальность', max_length=80, blank=True)


class Flight(models.Model):
    class Kind(models.TextChoices):
        DEPARTURE = 'departure', 'Вылет'
        ARRIVAL = 'arrival', 'Прилёт'

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'По расписанию'
        BOARDING = 'boarding', 'Посадка'
        DELAYED = 'delayed', 'Задержан'
        DEPARTED = 'departed', 'Вылетел'

    number = models.CharField('Номер рейса', max_length=12)
    airline = models.CharField('Авиакомпания', max_length=100)
    origin = models.CharField('Город отправления', max_length=100)
    origin_code = models.CharField('Код аэропорта отправления', max_length=3)
    destination = models.CharField('Город прибытия', max_length=100)
    destination_code = models.CharField('Код аэропорта прибытия', max_length=3)
    departure_at = models.DateTimeField('Вылет')
    arrival_at = models.DateTimeField('Прилёт')
    kind = models.CharField('Тип', max_length=10, choices=Kind.choices, default=Kind.DEPARTURE)
    gate = models.CharField('Гейт', max_length=8)
    status = models.CharField('Статус', max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    aircraft = models.CharField('Самолёт', max_length=80, default='Airbus A320')
    capacity = models.PositiveIntegerField('Количество мест', default=180, validators=[MinValueValidator(1)])
    price = models.PositiveIntegerField('Стоимость, ₽', default=7500)

    class Meta:
        ordering = ['departure_at', 'pk']
        verbose_name = 'рейс'
        verbose_name_plural = 'рейсы'
        constraints = [models.UniqueConstraint(fields=['number', 'departure_at'], name='unique_flight_departure')]

    def __str__(self):
        return f'{self.number} · {self.origin} — {self.destination}'

    def clean(self):
        if self.departure_at and self.arrival_at and self.arrival_at <= self.departure_at:
            raise ValidationError({'arrival_at': 'Прилёт должен быть позже вылета.'})

    @property
    def duration(self):
        minutes = int((self.arrival_at - self.departure_at).total_seconds() // 60)
        return f'{minutes // 60} ч {minutes % 60:02d} мин'

    @property
    def available_seats(self):
        return self.capacity - self.bookings.count()

    @property
    def can_book(self):
        return self.departure_at > timezone.now() and self.status != self.Status.DEPARTED and self.available_seats > 0


class Booking(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='bookings', verbose_name='Рейс')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings', verbose_name='Пользователь')
    passenger_name = models.CharField('Имя и фамилия пассажира', max_length=150)
    seat = models.CharField('Место', max_length=4)
    ticket_number = models.CharField('Номер билета', max_length=30, blank=True)
    checked_in = models.BooleanField('Зарегистрирован на рейс', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'бронирование'
        verbose_name_plural = 'бронирования'
        constraints = [
            models.UniqueConstraint(fields=['flight', 'seat'], name='unique_flight_seat'),
            models.UniqueConstraint(fields=['flight', 'user'], name='unique_user_flight'),
        ]

    def __str__(self):
        return f'{self.flight.number} · {self.passenger_name} · {self.seat}'

    def clean(self):
        if self.checked_in and not self.ticket_number.strip():
            raise ValidationError({'ticket_number': 'Для регистрации на рейс укажите номер билета.'})
        if self.flight_id and self.seat:
            row, letter = self.seat[:-1], self.seat[-1:]
            if not row.isdigit() or letter not in 'ABCDEF' or not 0 <= (int(row) - 1) * 6 + 'ABCDEF'.index(letter) < self.flight.capacity:
                raise ValidationError({'seat': 'Такого места нет в салоне самолёта.'})


class Review(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='reviews', verbose_name='Рейс')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')
    flight_date = models.DateField('Дата рейса')
    text = models.TextField('Ваш отзыв')
    rating = models.PositiveSmallIntegerField('Оценка', validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'

    def __str__(self):
        return f'{self.flight.number} · {self.rating}/10'
