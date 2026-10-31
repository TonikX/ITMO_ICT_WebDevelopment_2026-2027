"""Модели приложения "Доска домашних заданий"."""

from django.conf import settings
from django.db import models


class Homework(models.Model):
    """Домашнее задание."""

    subject = models.CharField('Предмет', max_length=120)
    teacher = models.CharField('Преподаватель', max_length=120)
    issue_date = models.DateField('Дата выдачи')
    deadline = models.DateField('Срок сдачи (период выполнения)')
    text = models.TextField('Текст задания')
    penalty_info = models.TextField('Информация о штрафах', blank=True)

    class Meta:
        ordering = ['deadline', 'issue_date']
        verbose_name = 'домашнее задание'
        verbose_name_plural = 'домашние задания'

    def __str__(self):
        return f'{self.subject} — {self.teacher}'


class Submission(models.Model):
    """Решение ученика, сданное текстом."""

    homework = models.ForeignKey(
        Homework, on_delete=models.CASCADE, related_name='submissions',
        verbose_name='Задание',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions',
        verbose_name='Ученик',
    )
    text = models.TextField('Текст решения')
    submitted_at = models.DateTimeField('Время сдачи', auto_now_add=True)
    mark = models.PositiveSmallIntegerField(
        'Отметка', null=True, blank=True,
        help_text='Выставляет преподаватель в панели администратора.',
    )
    marked_at = models.DateTimeField('Дата выставления отметки', null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['homework', 'student'],
                name='one_submission_per_homework',
            ),
        ]
        ordering = ['-submitted_at']
        verbose_name = 'сданная работа'
        verbose_name_plural = 'сданные работы'

    def __str__(self):
        return f'{self.student} — {self.homework} ({self.submitted_at:%d.%m.%Y})'


class Profile(models.Model):
    """Дополнительные данные пользователя: учебная группа (класс)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile',
        verbose_name='Пользователь',
    )
    group = models.CharField('Класс / учебная группа', max_length=60, blank=True)

    class Meta:
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'профили пользователей'

    def __str__(self):
        return f'{self.user.username} ({self.group or "группа не указана"})'
