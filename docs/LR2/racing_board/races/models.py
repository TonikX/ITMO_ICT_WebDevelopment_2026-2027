from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return self.username


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Car(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    car_number = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.brand} {self.model} ({self.car_number})'


class DriverProfile(models.Model):
    CLASS_CHOICES = [
        ('amateur', 'Любитель'),
        ('semi_pro', 'Полупрофессионал'),
        ('professional', 'Профессионал'),
    ]

    user = models.OneToOneField(
        'races.User',
        on_delete=models.CASCADE,
        related_name='driver_profile'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='drivers'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='drivers'
    )
    description = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    driver_class = models.CharField(
        max_length=20,
        choices=CLASS_CHOICES,
        default='amateur'
    )

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username}'

class Race(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    is_registration_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Registration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Подтверждена'),
        ('rejected', 'Отклонена'),
    ]

    driver = models.ForeignKey(
        DriverProfile,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['driver', 'race'],
                name='unique_driver_race_registration'
            )
        ]

    def __str__(self):
        return f'{self.driver} — {self.race}'


class RaceResult(models.Model):
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='result'
    )
    heat_number = models.PositiveIntegerField(default=1)
    finish_time = models.DurationField(null=True, blank=True)
    position = models.PositiveIntegerField(null=True, blank=True)
    points = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.registration} — заезд {self.heat_number}'


class Comment(models.Model):
    TYPE_CHOICES = [
        ('cooperation', 'Вопрос о сотрудничестве'),
        ('racing', 'Вопрос о гонках'),
        ('other', 'Иное'),
    ]

    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        'races.User',
        on_delete=models.CASCADE,
        related_name='race_comments'
    )
    comment_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='other'
    )
    text = models.TextField()
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=10),
                name='comment_rating_between_1_and_10'
            )
        ]

    def __str__(self):
        return f'{self.author} — {self.race}'