from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Amenity(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Удобство'
        verbose_name_plural = 'Удобства'
        ordering = ['name']

    def __str__(self):
        return self.name


class Hotel(models.Model):
    name = models.CharField('Название', max_length=200)
    owner = models.CharField('Владелец', max_length=200)
    city = models.CharField('Город', max_length=100)
    address = models.CharField('Адрес', max_length=300)
    description = models.TextField('Описание', blank=True)
    amenities = models.ManyToManyField(Amenity, verbose_name='Удобства отеля', blank=True)

    class Meta:
        verbose_name = 'Отель'
        verbose_name_plural = 'Отели'
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(models.Model):
    TYPES = [
        ('single', 'Одноместный'),
        ('double', 'Двухместный'),
        ('family', 'Семейный'),
        ('suite', 'Люкс'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms', verbose_name='Отель')
    number = models.CharField('Номер', max_length=10)
    room_type = models.CharField('Тип', max_length=20, choices=TYPES)
    price = models.DecimalField('Цена за ночь', max_digits=8, decimal_places=2)
    capacity = models.PositiveSmallIntegerField('Вместимость', validators=[MinValueValidator(1)])
    amenities = models.ManyToManyField(Amenity, verbose_name='Удобства в номере', blank=True)

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'
        ordering = ['hotel', 'number']
        unique_together = ['hotel', 'number']

    def __str__(self):
        return f'{self.hotel.name}, номер {self.number}'


class Reservation(models.Model):
    STATUSES = [
        ('booked', 'Забронировано'),
        ('checked_in', 'Заселен'),
        ('checked_out', 'Выселен'),
        ('cancelled', 'Отменено'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations', verbose_name='Гость')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations', verbose_name='Номер')
    date_from = models.DateField('Дата заезда')
    date_to = models.DateField('Дата выезда')
    guests = models.PositiveSmallIntegerField('Количество гостей', default=1, validators=[MinValueValidator(1)])
    status = models.CharField('Статус', max_length=20, choices=STATUSES, default='booked')
    checked_in_at = models.DateTimeField('Время заселения', null=True, blank=True)
    checked_out_at = models.DateTimeField('Время выселения', null=True, blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-date_from']

    def __str__(self):
        return f'{self.user} - {self.room} ({self.date_from} - {self.date_to})'

    @property
    def nights(self):
        return (self.date_to - self.date_from).days

    @property
    def total_price(self):
        return self.room.price * self.nights

    def can_edit(self):
        return self.status == 'booked'


class Review(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews', verbose_name='Номер')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name='Автор')
    date_from = models.DateField('Проживание с')
    date_to = models.DateField('Проживание по')
    text = models.TextField('Текст отзыва')
    rating = models.PositiveSmallIntegerField('Рейтинг', validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField('Дата отзыва', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} о {self.room}: {self.rating}/10'
