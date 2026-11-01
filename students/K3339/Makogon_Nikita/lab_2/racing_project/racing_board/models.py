from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# профиль участника (расширенный AbstractUser)
class RacerUser(AbstractUser):
    CLASS_CHOICES = [
        ('A', 'Класс A (Новички)'),
        ('B', 'Класс B (Любители)'),
        ('PRO', 'Класс PRO (Профессионалы)'),
        ('GT3', 'Класс GT3 (Суперкары)'),
    ]
    full_name = models.CharField(max_length=150, verbose_name="ФИО участника")
    team_name = models.CharField(max_length=100, blank=True, verbose_name="Название команды")
    car_description = models.TextField(blank=True, verbose_name="Описание автомобиля")
    racer_description = models.TextField(blank=True, verbose_name="Описание участника")
    experience = models.PositiveIntegerField(default=0, verbose_name="Опыт (лет)")
    racer_class = models.CharField(
        max_length=10,
        choices=CLASS_CHOICES,
        default='A',
        verbose_name="Класс участника"
    )

    class Meta:
        verbose_name = "Участник автогонок"
        verbose_name_plural = "Участники автогонок"
        ordering = ['-experience', 'full_name']

    def __str__(self):
        return f"{self.full_name or self.username} ({self.team_name or 'Индивидуальный'})"


# заезд
class Race(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название гонки")
    track = models.CharField(max_length=150, verbose_name="Трасса")
    race_date = models.DateField(verbose_name="Дата заезда")
    description = models.TextField(verbose_name="Описание")
    is_completed = models.BooleanField(default=False, verbose_name="Гонка завершена")

    class Meta:
        verbose_name = "Автогонка"
        verbose_name_plural = "Автогонки"
        ordering = ['-race_date']

    def __str__(self):
        return f"{self.title} ({self.race_date})"


# регистрация гонщика на гонку + результаты заезда
class RaceRegistration(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='registrations', verbose_name="Автогонка")
    racer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations', verbose_name="Гонщик")
    car_number = models.PositiveIntegerField(verbose_name="Бортовой номер")
    racer_comment = models.CharField(max_length=255, blank=True, verbose_name="Заметка к заезду")

    # поля времени и результата для администратора
    race_time = models.CharField(max_length=50, blank=True, null=True, verbose_name="Время заезда (чч:мм:сс.мс)")
    result_place = models.PositiveIntegerField(blank=True, null=True, verbose_name="Итоговое место")
    result_status = models.CharField(max_length=50, default="Зарегистрирован", verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подачи заявки")

    class Meta:
        verbose_name = "Регистрация и результат"
        verbose_name_plural = "Регистрации и результаты"
        unique_together = ('race', 'racer')
        ordering = ['result_place', 'race_time', 'car_number']

    def __str__(self):
        return f"{self.racer} -> {self.race} [№{self.car_number}]"


# отзывы и комментарии к гонкам
class Comment(models.Model):
    COMMENT_TYPES = [
        ('cooperation', 'Вопрос о сотрудничестве'),
        ('race_question', 'Вопрос о гонках'),
        ('other', 'Иное'),
    ]
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='comments', verbose_name="Автогонка")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', verbose_name="Комментатор")
    race_date = models.DateField(verbose_name="Дата заезда")
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPES, verbose_name="Тип комментария")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Рейтинг (1-10)"
    )
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.author} к {self.race} ({self.rating}/10)"