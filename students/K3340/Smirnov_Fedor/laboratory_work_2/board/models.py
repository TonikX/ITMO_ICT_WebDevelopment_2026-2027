from django.conf import settings
from django.db import models


class Flight(models.Model):
    KINDS = (
        ('departure', 'Вылет'),
        ('arrival', 'Прилёт'),
    )

    number = models.CharField('Номер рейса', max_length=10)
    airline = models.CharField('Авиакомпания', max_length=100)
    kind = models.CharField('Тип', max_length=10, choices=KINDS)
    from_city = models.CharField('Откуда', max_length=100)
    to_city = models.CharField('Куда', max_length=100)
    takeoff = models.DateTimeField('Вылет')
    landing = models.DateTimeField('Прилёт')
    gate = models.CharField('Гейт', max_length=5)
    seats = models.PositiveIntegerField('Мест в самолёте')

    class Meta:
        ordering = ['takeoff']
        verbose_name = 'рейс'
        verbose_name_plural = 'рейсы'

    def __str__(self):
        return f'{self.number} {self.from_city} — {self.to_city}'


class Booking(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='bookings', verbose_name='Рейс')
    passenger = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пассажир')
    seat = models.PositiveIntegerField('Место')
    ticket = models.CharField('Номер билета', max_length=20, blank=True)
    checked_in = models.BooleanField('Зарегистрирован', default=False)

    class Meta:
        unique_together = ['flight', 'seat']
        verbose_name = 'бронь'
        verbose_name_plural = 'брони'

    def __str__(self):
        return f'{self.flight.number}, место {self.seat}'


class Comment(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='comments', verbose_name='Рейс')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')
    flight_date = models.DateField('Дата рейса')
    text = models.TextField('Комментарий')
    rating = models.PositiveSmallIntegerField('Оценка', choices=[(n, n) for n in range(1, 11)])

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'

    def __str__(self):
        return f'{self.author} о рейсе {self.flight.number}'
