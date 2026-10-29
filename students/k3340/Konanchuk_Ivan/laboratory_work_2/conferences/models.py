from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    organization = models.CharField("Организация", max_length=200, blank=True)
    academic_degree = models.CharField("Учёная степень", max_length=100, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username


class Topic(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Тематика"
        verbose_name_plural = "Тематики"

    def __str__(self):
        return self.name


class Conference(models.Model):
    name = models.CharField("Название", max_length=200)
    topics = models.ManyToManyField(Topic, related_name="conferences", verbose_name="Тематики")
    venue = models.CharField("Место проведения", max_length=200)
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")
    description = models.TextField("Описание конференции")
    venue_description = models.TextField("Описание места проведения")
    conditions = models.TextField("Условия участия")

    class Meta:
        ordering = ["start_date"]
        verbose_name = "Конференция"
        verbose_name_plural = "Конференции"

    def __str__(self):
        return self.name


class Participation(models.Model):
    RESULT_CHOICES = [
        ("pending", "Не рассмотрен"),
        ("recommended", "Рекомендован к публикации"),
        ("rejected", "Не рекомендован"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="participations", verbose_name="Участник")
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE,
                                   related_name="participations", verbose_name="Конференция")
    talk_title = models.CharField("Тема доклада", max_length=300)
    abstract = models.TextField("Аннотация")
    result = models.CharField("Результат", max_length=20, choices=RESULT_CHOICES, default="pending")
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        ordering = ["conference__start_date", "user__last_name"]
        unique_together = ["user", "conference"]
        verbose_name = "Выступление"
        verbose_name_plural = "Выступления"

    def __str__(self):
        return f"{self.user}: {self.talk_title}"


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="reviews", verbose_name="Автор")
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE,
                                   related_name="reviews", verbose_name="Конференция")
    text = models.TextField("Текст отзыва")
    rating = models.PositiveSmallIntegerField(
        "Рейтинг", validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField("Дата отзыва", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.user} о {self.conference}"
