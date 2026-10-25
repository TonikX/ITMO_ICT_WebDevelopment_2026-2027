from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Tour(models.Model):
    places_total = models.PositiveIntegerField(default=10)
    title = models.CharField(max_length=100)
    agency = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField()

    start_date = models.DateField()
    end_date = models.DateField()

    payment_terms = models.TextField()

    @property
    def booked_places(self):
        return sum(
            booking.people_count
            for booking in self.bookings.all()
        )

    @property
    def available_places(self):
        return max(self.places_total - self.booked_places, 0)

    def __str__(self):
        return self.title

class Booking(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    people_count = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)



class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    text = models.TextField()

    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    tour_start_date = models.DateField(editable=False)
    tour_end_date = models.DateField(editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.tour_start_date = self.tour.start_date
            self.tour_end_date = self.tour.end_date

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} — {self.tour.title} — {self.rating}/10"