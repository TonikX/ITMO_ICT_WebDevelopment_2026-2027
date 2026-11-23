from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.db.models import Q, F
from django.urls import reverse
from django.utils import timezone


class Airline(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    code = models.CharField('Код', max_length=3, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Авиакомпания'
        verbose_name_plural = 'Авиакомпании'

    def __str__(self):
        return self.name


class Flight(models.Model):
    class Direction(models.TextChoices):
        DEPARTURE = 'departure', 'Вылет'
        ARRIVAL = 'arrival', 'Прилёт'

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'По расписанию'
        BOARDING = 'boarding', 'Посадка'
        DELAYED = 'delayed', 'Задержан'
        COMPLETED = 'completed', 'Завершён'
        CANCELLED = 'cancelled', 'Отменён'

    number = models.CharField('Номер рейса', max_length=12)
    airline = models.ForeignKey(Airline, on_delete=models.PROTECT, verbose_name='Авиакомпания')
    origin = models.CharField('Откуда', max_length=100)
    destination = models.CharField('Куда', max_length=100)
    departure_at = models.DateTimeField('Время вылета')
    arrival_at = models.DateTimeField('Время прилёта')
    direction = models.CharField('Тип', max_length=10, choices=Direction.choices)
    gate = models.CharField('Гейт', max_length=10)
    capacity = models.PositiveSmallIntegerField('Количество мест', validators=[MinValueValidator(1), MaxValueValidator(600)])
    status = models.CharField('Статус', max_length=12, choices=Status.choices, default=Status.SCHEDULED)

    class Meta:
        ordering = ['departure_at', 'number']
        indexes = [models.Index(fields=['departure_at', 'id'], name='flight_cursor_idx')]
        verbose_name = 'Рейс'
        verbose_name_plural = 'Рейсы'
        constraints = [
            models.UniqueConstraint(fields=['number', 'departure_at'], name='unique_flight_instance'),
            models.CheckConstraint(condition=Q(arrival_at__gt=F('departure_at')), name='flight_arrives_after_departure'),
            models.CheckConstraint(condition=Q(capacity__gte=1, capacity__lte=600), name='valid_flight_capacity'),
        ]

    def __str__(self):
        return f'{self.number} · {self.origin} → {self.destination}'

    def get_absolute_url(self):
        return reverse('flight_detail', args=[self.pk])

    @property
    def is_bookable(self):
        return self.departure_at > timezone.now() and self.status in {
            self.Status.SCHEDULED, self.Status.DELAYED, self.Status.BOARDING}

    def clean(self):
        if self.arrival_at and self.departure_at and self.arrival_at <= self.departure_at:
            raise ValidationError({'arrival_at': 'Прилёт должен быть позже вылета.'})
        if self.pk and self.capacity and self.bookings.filter(seat__gt=self.capacity).exists():
            raise ValidationError({'capacity': 'Нельзя убрать уже забронированные места.'})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:
                Flight.objects.select_for_update().get(pk=self.pk)
            self.full_clean()
            return super().save(*args, **kwargs)


class Booking(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.PROTECT, related_name='bookings', verbose_name='Рейс')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings', verbose_name='Пользователь')
    passenger_name = models.CharField('Имя и фамилия пассажира', max_length=100)
    seat = models.PositiveSmallIntegerField('Место', validators=[MinValueValidator(1)])
    ticket_number = models.CharField('Номер билета', max_length=30, blank=True, null=True, unique=True)
    checked_in = models.BooleanField('Зарегистрирован на рейс', default=False)
    created_at = models.DateTimeField('Дата бронирования', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        constraints = [
            models.UniqueConstraint(fields=['flight', 'seat'], name='unique_flight_seat'),
            models.UniqueConstraint(fields=['flight', 'user'], name='unique_user_flight_booking'),
            models.CheckConstraint(condition=Q(seat__gte=1), name='positive_seat'),
            models.CheckConstraint(condition=Q(checked_in=False) | (Q(ticket_number__isnull=False) & ~Q(ticket_number='')), name='checkin_requires_ticket'),
        ]

    def __str__(self):
        return f'{self.flight.number} · {self.passenger_name} · место {self.seat}'

    def clean(self):
        self.ticket_number = (self.ticket_number or '').strip() or None
        if self.checked_in and not self.ticket_number:
            raise ValidationError({'ticket_number': 'Для регистрации на рейс нужен номер билета.'})
        if not self.flight_id:
            return
        # Re-fetch: ModelForm may hold a stale flight from before the row lock.
        flight = Flight.objects.get(pk=self.flight_id)
        if self.seat and self.seat > flight.capacity:
            raise ValidationError({'seat': f'Выберите место от 1 до {flight.capacity}.'})
        if self._state.adding and not flight.is_bookable:
            raise ValidationError('Бронирование закрыто: рейс вылетел, завершён или отменён.')

    def save(self, *args, **kwargs):
        # All booking writers, including Django-admin, lock the same Flight row.
        # Unique constraints are the final protection against a double booking.
        with transaction.atomic():
            ids = {self.flight_id}
            if self.pk:
                previous = Booking.objects.filter(pk=self.pk).values_list('flight_id', flat=True).first()
                if previous:
                    ids.add(previous)
            list(Flight.objects.select_for_update().filter(pk__in=ids).order_by('pk'))
            self.full_clean()
            return super().save(*args, **kwargs)


class Review(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='reviews', verbose_name='Рейс')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')
    flight_date = models.DateField('Дата рейса', editable=False)
    text = models.TextField('Отзыв', max_length=2000)
    rating = models.PositiveSmallIntegerField('Оценка', validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField('Дата отзыва', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(fields=['flight', 'user'], name='one_review_per_user_flight'),
            models.CheckConstraint(condition=Q(rating__gte=1, rating__lte=10), name='rating_1_to_10'),
        ]

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.flight_date = timezone.localtime(self.flight.departure_at).date()
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.flight.number}: {self.rating}/10'
