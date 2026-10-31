from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Tour(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название тура')
    agency = models.CharField(max_length=150, verbose_name='Турагентство')
    country = models.CharField(max_length=100, verbose_name='Страна')
    description = models.TextField(verbose_name='Описание тура')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    payment_terms = models.TextField(verbose_name='Условия оплаты')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Стоимость'
    )
    available_places = models.PositiveIntegerField(
        default=1,
        verbose_name='Доступные места'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тур'
        verbose_name_plural = 'Туры'


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает подтверждения'
        CONFIRMED = 'confirmed', 'Подтверждено'
        CANCELLED = 'cancelled', 'Отменено'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Пользователь'
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Тур'
    )
    booking_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата бронирования'
    )
    places = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество мест'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус'
    )

    def __str__(self):
        return f'{self.user.username} — {self.tour.title}'

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'


class Review(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Тур'
    )
    travel_start_date = models.DateField(
        verbose_name='Дата начала поездки'
    )
    travel_end_date = models.DateField(
        verbose_name='Дата окончания поездки'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
        verbose_name='Рейтинг (1–10)'
    )

    def __str__(self):
        return f'{self.tour.title} — {self.rating}/10'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'