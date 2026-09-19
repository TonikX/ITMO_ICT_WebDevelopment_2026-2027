from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    pass


class Race(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    date = models.DateField()

    class Meta:
        ordering = ["-date", "title"]

    def __str__(self):
        return self.title


class RaceEntry(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name="entries")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="race_entries")
    full_name = models.CharField(max_length=200)
    team_name = models.CharField(max_length=200)
    car_description = models.TextField()
    participant_description = models.TextField()
    experience = models.CharField(max_length=100)
    racer_class = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("race", "user")
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} — {self.race}"


class RaceResult(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name="results")
    entry = models.OneToOneField(RaceEntry, on_delete=models.CASCADE, related_name="result")
    finish_time = models.CharField(max_length=50)
    place = models.PositiveIntegerField()
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["place", "finish_time"]

    def __str__(self):
        return f"{self.race}: {self.place} — {self.entry.full_name}"


class RaceComment(models.Model):
    TYPE_COOP = "coop"
    TYPE_RACE = "race"
    TYPE_OTHER = "other"
    COMMENT_TYPES = (
        (TYPE_COOP, "вопрос о сотрудничестве"),
        (TYPE_RACE, "вопрос о гонках"),
        (TYPE_OTHER, "иное"),
    )

    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="race_comments")
    race_date = models.DateField()
    text = models.TextField()
    comment_type = models.CharField(max_length=10, choices=COMMENT_TYPES)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author} → {self.race}"
