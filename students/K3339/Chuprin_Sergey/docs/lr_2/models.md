# Модель данных

### Сущности

| Модель | Назначение | Связи |
|--------|------------|-------|
| `Topic` | Тематика конференции | — |
| `Conference` | Конференция: название, даты, место, описание, условия участия | M2M → `Topic` |
| `Registration` | Заявка автора на выступление: название доклада, аннотация, статус, результат | FK → `User`, FK → `Conference`, M2M → `Topic` |
| `Feedback` | Отзыв к конференции: текст, дата, рейтинг 1–10 | FK → `User`, FK → `Conference` |

Пользователи — стандартная модель `User` из `django.contrib.auth`.

У заявки есть статус (`На рассмотрении`, `Принята`, `Отклонена`) и поле
`is_recommended` — результат выступления (рекомендован к публикации или нет),
который выставляет администратор.

### Код моделей

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Conference(models.Model):
    name = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    place = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    conditions_of_participation = models.TextField()

    topics = models.ManyToManyField(Topic)

    def __str__(self):
        return self.name


# class User(models.Model):
#     ROLES = (
#         ('admin', 'Администратор'),
#         ('spectator', 'Зритель'),
#         ('author', 'Автор'),
#     )
#
#     name = models.CharField(max_length=200)
#     email = models.EmailField()
#     password_hash = models.CharField(max_length=200)
#     about_me = models.TextField()
#     role = models.CharField(max_length=9,choices=ROLES)
#     date_of_birth = models.DateTimeField()


class Feedback(models.Model):
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}: {self.rating}"


class Registration(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'На рассмотрении'
        APPROVED = 'approved', 'Принята'
        REJECTED = 'rejected', 'Отклонена'

    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    performance_time = models.DateTimeField(null=True, blank=True)
    is_recommended = models.BooleanField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    topics = models.ManyToManyField(Topic)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
```
