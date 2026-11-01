from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Topic(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Тематика"
        verbose_name_plural = "Тематики"

    def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField("Название", max_length=150)
    city = models.CharField("Город", max_length=80)
    address = models.CharField("Адрес", max_length=200)
    description = models.TextField("Описание места проведения")

    class Meta:
        ordering = ["city", "name"]
        verbose_name = "Место проведения"
        verbose_name_plural = "Места проведения"

    def __str__(self):
        return f"{self.name}, {self.city}"


class Conference(models.Model):
    title = models.CharField("Название", max_length=200)
    topics = models.ManyToManyField(Topic, related_name="conferences", verbose_name="Тематики")
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="conferences", verbose_name="Место проведения")
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")
    description = models.TextField("Описание конференции")
    participation_terms = models.TextField("Условия участия")

    class Meta:
        ordering = ["start_date", "pk"]
        verbose_name = "Конференция"
        verbose_name_plural = "Конференции"

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "Дата окончания должна быть не раньше даты начала."})

    def __str__(self):
        return self.title


class Registration(models.Model):
    class Result(models.TextChoices):
        PENDING = "pending", "Ожидает решения"
        RECOMMENDED = "recommended", "Рекомендован к публикации"
        NOT_RECOMMENDED = "not_recommended", "Не рекомендован к публикации"

    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name="registrations", verbose_name="Конференция")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registrations", verbose_name="Автор")
    presentation_title = models.CharField("Тема выступления", max_length=200)
    affiliation = models.CharField("Организация", max_length=150)
    abstract = models.TextField("Аннотация", blank=True)
    result = models.CharField("Результат выступления", max_length=20, choices=Result.choices, default=Result.PENDING)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        ordering = ["conference__start_date", "author__last_name", "pk"]
        constraints = [models.UniqueConstraint(fields=["conference", "author"], name="unique_conference_author")]
        verbose_name = "Заявка на выступление"
        verbose_name_plural = "Заявки на выступления"

    def __str__(self):
        return f"{self.author} — {self.conference}"


class Review(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name="reviews", verbose_name="Конференция")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор")
    conference_start = models.DateField("Начало конференции")
    conference_end = models.DateField("Окончание конференции")
    text = models.TextField("Отзыв")
    rating = models.PositiveSmallIntegerField("Оценка", validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField("Дата отзыва", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        constraints = [models.UniqueConstraint(fields=["conference", "author"], name="unique_conference_review")]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.conference}: {self.rating}/10"
