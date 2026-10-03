from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=150)
    owner_name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Amenity(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Room(models.Model):
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='rooms'
    )

    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        related_name='rooms'
    )

    number = models.CharField(max_length=20)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    capacity = models.PositiveIntegerField()

    amenities = models.ManyToManyField(
        Amenity,
        related_name='rooms',
        blank=True
    )

    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.hotel.name} — номер {self.number}'


class Reservation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations'
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='reservations'
    )

    check_in = models.DateField()
    check_out = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} — {self.room} ({self.check_in} - {self.check_out})'


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    stay_from = models.DateField()
    stay_to = models.DateField()

    text = models.TextField()

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Отзыв {self.user} — {self.room}'


class Stay(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stays'
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='stays'
    )

    check_in = models.DateTimeField()
    check_out = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.user} — {self.room}'