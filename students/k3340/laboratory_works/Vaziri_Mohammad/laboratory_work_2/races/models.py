"""Модель данных «Табло победителей автогонок» (ЛР2, вариант 6).

Team      — команда.
Racer     — участник (гонщик): ФИО, команда, описание, опыт, класс; профиль пользователя.
Race      — автогонка.
Registration — регистрация гонщика на гонку: стартовый номер и автомобиль на эту гонку.
Heat      — заезд гонки; время заезда задаёт администратор.
Result    — результат участника в заезде (место, время, статус); задаёт администратор.
Comment   — отзыв или комментарий к гонке от зарегистрированного пользователя.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Team(models.Model):
    name = models.CharField("Название команды", max_length=100, unique=True)
    country = models.CharField("Страна", max_length=60, blank=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Команда"
        verbose_name_plural = "Команды"

    def __str__(self):
        return self.name


class Racer(models.Model):
    class RacerClass(models.TextChoices):
        ROOKIE = "rookie", "Новичок"
        AMATEUR = "amateur", "Любитель"
        PRO = "pro", "Профессионал"
        ELITE = "elite", "Элита"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="racer",
        verbose_name="Пользователь",
    )
    full_name = models.CharField("ФИО участника", max_length=150)
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="racers",
        verbose_name="Команда",
    )
    description = models.TextField("Описание участника", blank=True)
    experience_years = models.PositiveSmallIntegerField(
        "Опыт, лет", default=0, validators=[MaxValueValidator(80)]
    )
    racer_class = models.CharField(
        "Класс участника", max_length=10, choices=RacerClass.choices, default=RacerClass.ROOKIE
    )

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Гонщик"
        verbose_name_plural = "Гонщики"

    def __str__(self):
        return self.full_name


class Race(models.Model):
    title = models.CharField("Название", max_length=150)
    track = models.CharField("Трасса / место проведения", max_length=150)
    date = models.DateField("Дата гонки")
    description = models.TextField("Описание", blank=True)
    registration_open = models.BooleanField("Регистрация открыта", default=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Автогонка"
        verbose_name_plural = "Автогонки"

    def __str__(self):
        return f"{self.title} ({self.date:%d.%m.%Y})"

    def get_absolute_url(self):
        return reverse("race_detail", args=[self.pk])

    @property
    def is_upcoming(self):
        return self.date >= timezone.localdate()

    def registration_is_open(self):
        return self.registration_open and self.is_upcoming


class Registration(models.Model):
    race = models.ForeignKey(
        Race, on_delete=models.CASCADE, related_name="registrations", verbose_name="Гонка"
    )
    racer = models.ForeignKey(
        Racer, on_delete=models.CASCADE, related_name="registrations", verbose_name="Гонщик"
    )
    car_number = models.PositiveSmallIntegerField(
        "Стартовый номер", validators=[MinValueValidator(1), MaxValueValidator(999)]
    )
    car_description = models.CharField("Автомобиль", max_length=200)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        ordering = ["race", "car_number"]
        verbose_name = "Регистрация на гонку"
        verbose_name_plural = "Регистрации на гонки"
        constraints = [
            models.UniqueConstraint(fields=["race", "racer"], name="unique_racer_per_race"),
            models.UniqueConstraint(fields=["race", "car_number"], name="unique_car_number_per_race"),
        ]

    def __str__(self):
        return f"#{self.car_number} {self.racer}"

    def can_be_changed(self):
        """Свою регистрацию можно менять, пока гонка не прошла и нет результатов."""
        return self.race.is_upcoming and not self.results.exists()


class Heat(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name="heats", verbose_name="Гонка")
    number = models.PositiveSmallIntegerField("Номер заезда", validators=[MinValueValidator(1)])
    name = models.CharField("Название заезда", max_length=60, blank=True)
    start_time = models.DateTimeField("Время заезда", null=True, blank=True)
    laps = models.PositiveSmallIntegerField("Количество кругов", default=10)

    class Meta:
        ordering = ["race", "number"]
        verbose_name = "Заезд"
        verbose_name_plural = "Заезды"
        constraints = [
            models.UniqueConstraint(fields=["race", "number"], name="unique_heat_number_per_race"),
        ]

    def __str__(self):
        label = self.name or f"Заезд {self.number}"
        return f"{self.race.title}: {label}"


class Result(models.Model):
    class Status(models.TextChoices):
        FINISHED = "finished", "Финишировал"
        DNF = "dnf", "Сошёл"
        DSQ = "dsq", "Дисквалифицирован"

    heat = models.ForeignKey(Heat, on_delete=models.CASCADE, related_name="results", verbose_name="Заезд")
    registration = models.ForeignKey(
        Registration, on_delete=models.CASCADE, related_name="results", verbose_name="Участник"
    )
    position = models.PositiveSmallIntegerField(
        "Место", null=True, blank=True, validators=[MinValueValidator(1)]
    )
    finish_time = models.DurationField("Время", null=True, blank=True, help_text="Например 12:34.567")
    status = models.CharField("Статус", max_length=10, choices=Status.choices, default=Status.FINISHED)

    class Meta:
        ordering = ["heat", "position"]
        verbose_name = "Результат"
        verbose_name_plural = "Результаты"
        constraints = [
            models.UniqueConstraint(fields=["heat", "registration"], name="unique_result_per_heat"),
        ]

    def __str__(self):
        return f"{self.heat}: {self.registration} — {self.position or self.get_status_display()}"

    def clean(self):
        if self.heat_id and self.registration_id and self.registration.race_id != self.heat.race_id:
            raise ValidationError("Участник зарегистрирован на другую гонку.")
        if self.status == self.Status.FINISHED and self.position is None:
            raise ValidationError({"position": "Для финишировавшего участника укажите место."})


class Comment(models.Model):
    class CommentType(models.TextChoices):
        COOPERATION = "cooperation", "Вопрос о сотрудничестве"
        RACING = "racing", "Вопрос о гонках"
        OTHER = "other", "Иное"

    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name="comments", verbose_name="Гонка")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="race_comments",
        verbose_name="Комментатор",
    )
    heat_date = models.DateField("Дата заезда")
    text = models.TextField("Текст комментария")
    comment_type = models.CharField(
        "Тип комментария", max_length=12, choices=CommentType.choices, default=CommentType.RACING
    )
    rating = models.PositiveSmallIntegerField(
        "Рейтинг", validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"{self.author} → {self.race.title} ({self.rating}/10)"
