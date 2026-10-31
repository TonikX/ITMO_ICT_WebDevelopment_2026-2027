"""Модель конференций, выступлений и отзывов."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Topic(models.Model):
    """Тематика конференции."""

    name = models.CharField("Название", max_length=120, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "тематика"
        verbose_name_plural = "тематики"

    def __str__(self) -> str:
        return self.name


class Conference(models.Model):
    """Конференция с условиями участия и периодом проведения."""

    title = models.CharField("Название", max_length=200)
    topics = models.ManyToManyField(
        Topic, verbose_name="Тематики", related_name="conferences"
    )
    location = models.CharField("Место проведения", max_length=200)
    start_date = models.DateField("Начало")
    end_date = models.DateField("Окончание")
    description = models.TextField("Описание конференции")
    venue_description = models.TextField("Описание места проведения")
    participation_terms = models.TextField("Условия участия")

    class Meta:
        ordering = ["start_date", "pk"]
        verbose_name = "конференция"
        verbose_name_plural = "конференции"
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F("start_date")),
                name="conference_date_order",
            )
        ]

    def clean(self) -> None:
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {"end_date": "Окончание не может быть раньше начала."}
            )

    def __str__(self) -> str:
        return self.title


class Registration(models.Model):
    """Регистрация автора и результат его выступления."""

    class Result(models.TextChoices):
        PENDING = "pending", "Не рассмотрено"
        RECOMMENDED = "recommended", "Рекомендовано к публикации"
        REJECTED = "rejected", "Не рекомендовано к публикации"

    conference = models.ForeignKey(
        Conference,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="Конференция",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор"
    )
    presentation_title = models.CharField("Тема выступления", max_length=200)
    abstract = models.TextField("Аннотация")
    result = models.CharField(
        "Результат", max_length=16, choices=Result.choices, default=Result.PENDING
    )

    class Meta:
        ordering = ["conference__start_date", "pk"]
        verbose_name = "регистрация выступления"
        verbose_name_plural = "регистрации выступлений"
        constraints = [
            models.UniqueConstraint(
                fields=["conference", "author"], name="unique_conference_author"
            ),
            models.CheckConstraint(
                check=models.Q(result__in=["pending", "recommended", "rejected"]),
                name="registration_result_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.author} — {self.presentation_title}"


class Review(models.Model):
    """Отзыв автора с сохранёнными датами конференции."""

    conference = models.ForeignKey(
        Conference,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Конференция",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор"
    )
    start_date = models.DateField("Начало конференции")
    end_date = models.DateField("Окончание конференции")
    text = models.TextField("Текст отзыва")
    rating = models.PositiveSmallIntegerField(
        "Рейтинг", validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        ordering = ["-pk"]
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1, rating__lte=10),
                name="review_rating_range",
            ),
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F("start_date")),
                name="review_date_order",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.author}: {self.rating}/10"
