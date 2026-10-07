from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class User(AbstractUser):
    team = models.CharField(max_length=100, null=True, blank=True, help_text="Команда")
    experience = models.PositiveIntegerField(default=0, help_text="Опыт в годах")
    driver_class = models.CharField(max_length=50, null=True, blank=True, help_text="Класс участника")
    bio = models.TextField(null=True, blank=True, help_text="Описание участника")

    def __str__(self):
        return self.username

class Race(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    date = models.DateField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.name} ({self.date})'

class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='registrations')
    car_description = models.TextField(blank=True, help_text="автомобиль на эту гонку")
    race_time = models.CharField(max_length=20, blank=True, help_text="время заезда (заполняется администратором)")
    result = models.CharField(max_length=200, blank=True, help_text="результат заезда (заполняется администратором)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'race')

    def __str__(self):
        return f'{self.user.username} - ({self.race.name})'

class Comment(models.Model):
    TYPE_COOPERATION = 'coop'
    TYPE_RACE = 'race'
    TYPE_OTHER = 'other'
    TYPE_CHOICES = (
        (TYPE_COOPERATION, 'вопрос о сотрудничестве'),
        (TYPE_RACE, 'вопрос о гонках'),
        (TYPE_OTHER, 'иное'),
    )

    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    comment_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username} о {self.race.name}'
