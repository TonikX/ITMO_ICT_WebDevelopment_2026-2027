from django.conf import settings
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class TourCompany(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tour company"
        verbose_name_plural = "Tour companies"

    def __str__(self):
        return self.name


class Tour(models.Model):
    title = models.CharField(max_length=200)
    
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="tours",
    )
    company = models.ForeignKey(
        TourCompany,
        on_delete=models.PROTECT,
        related_name="tours",
    )
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_places = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    main_image = models.ImageField(
        upload_to="tours/main/",
        blank=True,
        null=True,
        verbose_name="Главное изображение",
    )    

    class Meta:
        ordering = ["start_date"]
        verbose_name = "Tour"
        verbose_name_plural = "Tours"

    def __str__(self):
        return self.title


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    booking_date = models.DateTimeField(auto_now_add=True)
    people_count = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        ordering = ["-booking_date"]
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def __str__(self):
        return f"{self.user} - {self.tour}"


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
    review_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ]
    )

    class Meta:
        ordering = ["-review_date"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self):
        return f"{self.tour} - {self.score}/10"


class TourImage(models.Model):
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Тур",
    )

    image = models.ImageField(
        upload_to="tours/gallery/",
        verbose_name="Изображение",
    )

    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Подпись",
    )

    class Meta:
        verbose_name = "Дополнительное изображение тура"
        verbose_name_plural = "Дополнительные изображения туров"

    def __str__(self):
        return f"Изображение тура: {self.tour.title}"
