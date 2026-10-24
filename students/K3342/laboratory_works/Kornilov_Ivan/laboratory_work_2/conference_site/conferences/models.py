from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Topic(models.Model):
    name = models.CharField('Тематика', max_length=120, unique=True)

    class Meta:
        verbose_name = 'Тематика'
        verbose_name_plural = 'Тематики'
        ordering = ['name']

    def __str__(self):
        return self.name


class Conference(models.Model):
    title = models.CharField('Название', max_length=200)
    topics = models.ManyToManyField(Topic, related_name='conferences', verbose_name='Тематики')
    venue_name = models.CharField('Место проведения', max_length=200)
    venue_description = models.TextField('Описание места проведения')
    start_date = models.DateField('Начало')
    end_date = models.DateField('Окончание')
    description = models.TextField('Описание конференции')
    participation_terms = models.TextField('Условия участия')

    class Meta:
        verbose_name = 'Конференция'
        verbose_name_plural = 'Конференции'
        ordering = ['start_date', 'title']

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError('Дата окончания не может быть раньше даты начала.')


class TalkRegistration(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='talks',
        verbose_name='Автор',
    )
    conference = models.ForeignKey(
        Conference,
        on_delete=models.CASCADE,
        related_name='talks',
        verbose_name='Конференция',
    )
    talk_title = models.CharField('Название доклада', max_length=200)
    abstract = models.TextField('Тезисы')
    recommended_for_publication = models.BooleanField(
        'Рекомендован к публикации',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Регистрация на выступление'
        verbose_name_plural = 'Регистрации на выступления'
        ordering = ['conference', 'talk_title']

    def __str__(self):
        return f'{self.talk_title} — {self.user}'

    def publication_label(self):
        if self.recommended_for_publication is True:
            return 'Рекомендован к публикации'
        if self.recommended_for_publication is False:
            return 'Не рекомендован'
        return 'Результат не указан'


class Review(models.Model):
    conference = models.ForeignKey(
        Conference,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Конференция',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conference_reviews',
        verbose_name='Автор отзыва',
    )
    conference_start = models.DateField('Начало конференции')
    conference_end = models.DateField('Окончание конференции')
    text = models.TextField('Текст отзыва')
    rating = models.PositiveSmallIntegerField(
        'Рейтинг',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author} — {self.conference} ({self.rating})'
