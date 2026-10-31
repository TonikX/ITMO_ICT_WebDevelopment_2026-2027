from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    passport_number = models.CharField(max_length=20, blank=True)
    home_address = models.TextField(blank=True)
    nationality = models.CharField(max_length=50, blank=True)


class Airline(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Flight(models.Model):
    TYPE_CHOICES = (
        ('departure', 'Отлёт'),
        ('arrival', 'Прилёт'),
    )
    number = models.CharField(max_length=10)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    departure_city = models.CharField(max_length=100)
    arrival_city = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    flight_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    gate_number = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.number} ({self.departure_city} → {self.arrival_city})'


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    ticket_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'flight')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.flight.number}'


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    flight_date = models.DateField()
    text = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.flight.number} ({self.rating}/10)'
