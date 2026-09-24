from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Topic(models.Model):
    name = models.CharField('название', max_length=100, unique=True)

    class Meta:
        verbose_name = 'тематика'
        verbose_name_plural = 'тематики'

    def __str__(self):
        return self.name


class Conference(models.Model):
    title = models.CharField('название', max_length=200)
    topics = models.ManyToManyField(Topic, related_name='conferences', blank=True, verbose_name='тематики')
    venue_name = models.CharField('место проведения', max_length=200)
    venue_description = models.TextField('описание места проведения', blank=True)
    start_date = models.DateField('дата начала')
    end_date = models.DateField('дата окончания')
    description = models.TextField('описание', blank=True)
    participation_terms = models.TextField('условия участия', blank=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'конференция'
        verbose_name_plural = 'конференции'

    def __str__(self):
        return self.title


class Registration(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='registrations', verbose_name='конференция')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations', verbose_name='пользователь')
    talk_title = models.CharField('тема доклада', max_length=200)
    created_at = models.DateTimeField('дата регистрации', auto_now_add=True)
    # редактируется только в Django-admin, обычным пользователям недоступно
    recommended_for_publication = models.BooleanField('рекомендован к публикации', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'регистрация'
        verbose_name_plural = 'регистрации'

    def __str__(self):
        return f'{self.user} — {self.talk_title} ({self.conference})'


class Review(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='reviews', verbose_name='конференция')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name='автор')
    rating = models.PositiveSmallIntegerField('оценка', validators=[MinValueValidator(1), MaxValueValidator(10)])
    text = models.TextField('текст отзыва')
    created_at = models.DateTimeField('дата создания', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'

    def __str__(self):
        return f'{self.author} — {self.conference} ({self.rating}/10)'
