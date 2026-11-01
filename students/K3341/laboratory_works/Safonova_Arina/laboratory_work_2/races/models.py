from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Race(models.Model):
    name = models.CharField('Название', max_length=150)
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['start_date', 'id']
        verbose_name = 'Автогонка'
        verbose_name_plural = 'Автогонки'


class Registration(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, verbose_name='Автогонка')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    full_name = models.CharField('ФИО гонщика', max_length=150)
    team = models.CharField('Команда', max_length=100)
    car_description = models.TextField('Описание автомобиля')
    description = models.TextField('Описание участника')
    experience = models.PositiveIntegerField('Опыт (полных лет)')
    driver_class = models.CharField('Класс участника', max_length=50)
    race_time = models.DurationField('Время заезда', null=True, blank=True)
    result = models.CharField('Результат', max_length=100, blank=True)

    def __str__(self):
        return f'{self.full_name} — {self.race}'

    class Meta:
        ordering = ['id']
        verbose_name = 'Регистрация'
        verbose_name_plural = 'Регистрации'


class Comment(models.Model):
    TYPES = [('cooperation', 'Вопрос о сотрудничестве'), ('race', 'Вопрос о гонках'), ('other', 'Иное')]
    race = models.ForeignKey(Race, on_delete=models.CASCADE, verbose_name='Автогонка')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Комментатор')
    start_date = models.DateField('Дата начала заезда')
    end_date = models.DateField('Дата окончания заезда')
    text = models.TextField('Текст комментария')
    comment_type = models.CharField('Тип комментария', max_length=15, choices=TYPES)
    rating = models.PositiveSmallIntegerField('Рейтинг (1–10)', validators=[MinValueValidator(1), MaxValueValidator(10)])

    def __str__(self):
        return f'{self.user} — {self.race}'

    class Meta:
        ordering = ['-id']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
