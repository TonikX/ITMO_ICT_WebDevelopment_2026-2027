from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    display_name = models.CharField(max_length=50, blank=True, verbose_name="Отображаемое имя")

    def __str__(self):
        return self.display_name or self.username


class Team(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    city = models.CharField(max_length=100, verbose_name="Город")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"

    def __str__(self):
        return f"{self.name} из {self.city}"


class Player(models.Model):
    POSITION_CHOICES = [
        ('PG', 'Разыгрывающий'),
        ('SG', 'Атакующий защитник'),
        ('SF', 'Легкий форвард'),
        ('PF', 'Тяжелый форвард'),
        ('C', 'Центровой'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players', verbose_name="Команда")
    full_name = models.CharField(max_length=150, verbose_name="ФИО")
    position = models.CharField(max_length=2, choices=POSITION_CHOICES, verbose_name="Позиция")
    number = models.PositiveIntegerField(verbose_name="Игровой номер")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"

    def __str__(self):
        return f"{self.full_name} (#{self.number})"


class Match(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Предстоящий'),
        ('finished', 'Завершенный'),
    ]

    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches', verbose_name="Хозяева")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches', verbose_name="Гости")
    date = models.DateTimeField(verbose_name="Дата и время")
    location = models.CharField(max_length=150, verbose_name="Место проведения")
    home_score = models.PositiveIntegerField(default=0, verbose_name="Очки хозяев")
    away_score = models.PositiveIntegerField(default=0, verbose_name="Очки гостей")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming', verbose_name="Статус")

    class Meta:
        verbose_name = "Матч"
        verbose_name_plural = "Матчи"

    def __str__(self):
        return f"{self.home_team} - {self.away_team} ({self.date.strftime('%Y-%m-%d')})"


class Prediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='predictions',
                             verbose_name="Пользователь")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='predictions', verbose_name="Матч")
    predicted_home_score = models.PositiveIntegerField(verbose_name="Прогноз очков хозяев")
    predicted_away_score = models.PositiveIntegerField(verbose_name="Прогноз очков гостей")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата прогноза")

    class Meta:
        verbose_name = "Прогноз"
        verbose_name_plural = "Прогнозы"
        unique_together = ('user', 'match')


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Автор")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='comments', verbose_name="Матч")
    text = models.TextField(verbose_name="Текст отзыва")
    rating = models.PositiveIntegerField(
        verbose_name="Рейтинг (1-10)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"