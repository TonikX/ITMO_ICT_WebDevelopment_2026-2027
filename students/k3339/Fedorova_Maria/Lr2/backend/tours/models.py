from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name

class Agency(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.name

class Tour(models.Model):
    name = models.CharField(max_length=200)
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name="tours",
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="tours",
    )
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    payment_terms = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def __str__(self) -> str:
        return self.name

class Reservation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user} — {self.tour}"

class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ]
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user} — {self.tour} — {self.rating}"
