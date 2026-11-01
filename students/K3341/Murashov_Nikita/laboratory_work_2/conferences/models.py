from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from .validators import RATING_VALIDATORS, validate_date_range


class User(AbstractUser):
    organization = models.CharField("Организация", max_length=200, blank=True)
    academic_degree = models.CharField("Учёная степень", max_length=100, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username


class Topic(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "тематика"
        verbose_name_plural = "тематики"

    def __str__(self):
        return self.name


class Conference(models.Model):
    title = models.CharField("Название", max_length=200)
    topics = models.ManyToManyField(Topic, verbose_name="Тематики", related_name="conferences")
    venue_name = models.CharField("Место проведения", max_length=200)
    city = models.CharField("Город", max_length=100)
    start_date = models.DateField("Начало")
    end_date = models.DateField("Окончание")
    description = models.TextField("Описание конференции")
    venue_description = models.TextField("Описание места проведения", blank=True)
    participation_terms = models.TextField("Условия участия")

    class Meta:
        ordering = ["start_date", "title"]
        verbose_name = "конференция"
        verbose_name_plural = "конференции"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("conference-detail", args=[self.pk])

    def clean(self):
        validate_date_range(self.start_date, self.end_date)


class Participation(models.Model):
    class Result(models.TextChoices):
        PENDING = "pending", "Не рассмотрено"
        RECOMMENDED = "recommended", "Рекомендован к публикации"
        NOT_RECOMMENDED = "not_recommended", "Не рекомендован к публикации"

    conference = models.ForeignKey(
        Conference, on_delete=models.CASCADE, related_name="participations", verbose_name="Конференция"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="participations", verbose_name="Автор"
    )
    talk_title = models.CharField("Название доклада", max_length=200)
    abstract = models.TextField("Тезисы доклада")
    result = models.CharField("Результат", max_length=20, choices=Result.choices, default=Result.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["conference", "user__last_name", "user__username"]
        constraints = [
            models.UniqueConstraint(fields=["conference", "user"], name="unique_participation_per_user")
        ]
        verbose_name = "регистрация"
        verbose_name_plural = "регистрации"

    def __str__(self):
        return f"{self.user} — {self.conference}"


class Review(models.Model):
    conference = models.ForeignKey(
        Conference, on_delete=models.CASCADE, related_name="reviews", verbose_name="Конференция"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews", verbose_name="Автор"
    )
    start_date = models.DateField("Дата начала участия")
    end_date = models.DateField("Дата окончания участия")
    text = models.TextField("Текст отзыва")
    rating = models.PositiveSmallIntegerField("Рейтинг", validators=RATING_VALIDATORS)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"

    def __str__(self):
        return f"{self.author}: {self.rating}/10 — {self.conference}"

    def clean(self):
        validate_date_range(self.start_date, self.end_date)
