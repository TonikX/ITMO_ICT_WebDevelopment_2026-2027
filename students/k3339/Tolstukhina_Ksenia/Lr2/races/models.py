from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    RACER_CLASSES = (
        ('pro', 'Профессионал'),
        ('am', 'Любитель'),
        ('junior', 'Юниор'),
    )

    racer_class = models.CharField(max_length=20, choices=RACER_CLASSES, blank=True)
    team = models.CharField(max_length=200, blank=True)
    birthday = models.DateField(null=True, blank=True)
    driving_experience = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class Auto(models.Model):
    state = models.CharField(max_length=15, unique=True)
    make = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    color = models.CharField(max_length=30)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='autos')
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.state})"


class Race(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=300, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.date})"


class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='results')
    auto = models.ForeignKey(Auto, on_delete=models.CASCADE, related_name='results')
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='results')
    duration = models.DurationField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} — {self.race}: {self.duration}"


class Registration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations')
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='registrations')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} → {self.race}"


class Comment(models.Model):
    COMMENT_TYPE = (
        ('cooperation', 'Вопрос о сотрудничестве'),
        ('race', 'Вопрос о гонках'),
        ('other', 'Иное'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    race_date = models.DateField()
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} → {self.race}: {self.text[:30]}"
