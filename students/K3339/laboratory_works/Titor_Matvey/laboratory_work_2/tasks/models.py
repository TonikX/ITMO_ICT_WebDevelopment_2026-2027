from django.conf import settings
from django.db import models


class Task(models.Model):
    discipline = models.CharField('Предмет', max_length=120)
    teacher_name = models.CharField('Преподаватель', max_length=120)
    issued_on = models.DateField('Дата выдачи')
    due_on = models.DateField('Срок выполнения')
    body = models.TextField('Задание')
    penalty = models.TextField('Штрафы за опоздание', blank=True)

    class Meta:
        ordering = ['due_on', 'issued_on']
        verbose_name = 'задание'
        verbose_name_plural = 'задания'

    def __str__(self):
        return f'{self.discipline}: {self.body[:40]}'


class Work(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='works',
        verbose_name='Задание',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='works',
        verbose_name='Ученик',
    )
    body = models.TextField('Текст решения')
    sent_at = models.DateTimeField('Отправлено', auto_now_add=True)
    score = models.PositiveSmallIntegerField('Отметка', null=True, blank=True)
    scored_at = models.DateTimeField('Отметка выставлена', null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['task', 'student'], name='one_work_per_task'),
        ]
        ordering = ['-sent_at']
        verbose_name = 'сданная работа'
        verbose_name_plural = 'сданные работы'

    def __str__(self):
        return f'{self.student} — {self.task}'


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='card',
        verbose_name='Пользователь',
    )
    study_group = models.CharField('Учебная группа', max_length=60, blank=True)

    class Meta:
        verbose_name = 'карточка ученика'
        verbose_name_plural = 'карточки учеников'

    def __str__(self):
        return f'{self.user.username} — {self.study_group or "без группы"}'
