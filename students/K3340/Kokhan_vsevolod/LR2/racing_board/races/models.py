from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')

    def __str__(self):
        return self.username


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

    def __str__(self):
        return self.name


class Car(models.Model):
    brand = models.CharField(max_length=100, verbose_name='Марка')
    model = models.CharField(max_length=100, verbose_name='Модель')
    car_number = models.CharField(max_length=20, unique=True, verbose_name='Номер')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

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
        related_name='driver_profile',
        verbose_name='Пользователь',
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='drivers',
        verbose_name='Команда',
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='drivers',
        verbose_name='Автомобиль',
    )
    description = models.TextField(blank=True, verbose_name='Описание участника')
    experience_years = models.PositiveIntegerField(default=0, verbose_name='Опыт (лет)')
    driver_class = models.CharField(
        max_length=20,
        choices=CLASS_CHOICES,
        default='amateur',
        verbose_name='Класс',
    )

    class Meta:
        verbose_name = 'Профиль гонщика'
        verbose_name_plural = 'Профили гонщиков'

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Race(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    location = models.CharField(max_length=200, verbose_name='Место проведения')
    start_date = models.DateTimeField(verbose_name='Дата начала')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания')
    is_registration_open = models.BooleanField(default=True, verbose_name='Регистрация открыта')

    class Meta:
        verbose_name = 'Гонка'
        verbose_name_plural = 'Гонки'
        ordering = ['start_date']

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
        related_name='registrations',
        verbose_name='Гонщик',
    )
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='Гонка',
    )
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заявки')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус',
    )
    comment = models.TextField(blank=True, verbose_name='Комментарий к заявке')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        constraints = [
            models.UniqueConstraint(
                fields=['driver', 'race'],
                name='unique_driver_race_registration',
            )
        ]

    def __str__(self):
        return f'{self.driver} — {self.race}'


class RaceResult(models.Model):
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='result',
        verbose_name='Заявка',
    )
    heat_number = models.PositiveIntegerField(default=1, verbose_name='Номер заезда')
    finish_time = models.DurationField(null=True, blank=True, verbose_name='Время финиша')
    position = models.PositiveIntegerField(null=True, blank=True, verbose_name='Место')
    points = models.PositiveIntegerField(default=0, verbose_name='Очки')
    notes = models.TextField(blank=True, verbose_name='Заметки')

    class Meta:
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'
        ordering = ['position', 'finish_time']

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
        related_name='comments',
        verbose_name='Гонка',
    )
    author = models.ForeignKey(
        'races.User',
        on_delete=models.CASCADE,
        related_name='race_comments',
        verbose_name='Автор',
    )
    comment_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='other',
        verbose_name='Тип комментария',
    )
    text = models.TextField(verbose_name='Текст')
    rating = models.PositiveSmallIntegerField(verbose_name='Рейтинг (1–10)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=10),
                name='comment_rating_between_1_and_10',
            )
        ]

    def __str__(self):
        return f'{self.author} — {self.race}'
