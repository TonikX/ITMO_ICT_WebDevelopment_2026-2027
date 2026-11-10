from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Agency(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    city = models.CharField(max_length=50, verbose_name='Город')

    class Meta:
        verbose_name = 'Турагентство'
        verbose_name_plural = 'Турагентства'

    def __str__(self):
        return self.name


class Tour(models.Model):
    agency = models.ForeignKey(
        Agency, on_delete=models.CASCADE, related_name='tours',
        verbose_name='Турагентство',
    )
    name = models.CharField(max_length=200, verbose_name='Название тура')
    country = models.CharField(max_length=50, verbose_name='Страна')
    description = models.TextField(verbose_name='Описание тура')
    date_start = models.DateField(verbose_name='Дата начала')
    date_end = models.DateField(verbose_name='Дата окончания')
    payment_terms = models.CharField(max_length=200, verbose_name='Условия оплаты')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена, руб.')

    class Meta:
        verbose_name = 'Тур'
        verbose_name_plural = 'Туры'

    def __str__(self):
        return f'{self.name} ({self.country})'


class Reservation(models.Model):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    STATUS_CHOICES = [
        (PENDING, 'ожидает подтверждения'),
        (CONFIRMED, 'подтверждено'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reservations', verbose_name='Пользователь',
    )
    tour = models.ForeignKey(
        Tour, on_delete=models.CASCADE, related_name='reservations',
        verbose_name='Тур',
    )
    guests = models.PositiveSmallIntegerField(default=1, verbose_name='Количество мест')
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=PENDING,
        verbose_name='Статус',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата бронирования')

    class Meta:
        verbose_name = 'Резервирование'
        verbose_name_plural = 'Резервирования'
        constraints = [
            models.UniqueConstraint(fields=['user', 'tour'], name='unique_user_tour'),
        ]

    def __str__(self):
        return f'{self.user} — {self.tour}'


class Review(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Автор',
    )
    tour = models.ForeignKey(
        Tour, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Тур',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Рейтинг (1-10)',
    )
    text = models.TextField(verbose_name='Текст отзыва')
    tour_date_start = models.DateField(verbose_name='Даты тура (начало)')
    tour_date_end = models.DateField(verbose_name='Даты тура (окончание)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(fields=['author', 'tour'], name='unique_author_tour'),
        ]

    def __str__(self):
        return f'{self.author} — {self.tour} ({self.rating}/10)'
