from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Driver(models.Model):
    CLASSES = [('PRO', 'PRO'), ('PRO-AM', 'PRO–AM'), ('AM', 'AM')]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driver')
    full_name = models.CharField('ФИО', max_length=150)
    team = models.CharField('Команда', max_length=100)
    car = models.CharField('Автомобиль и его характеристики', max_length=250)
    bio = models.TextField('Об участнике', max_length=1500)
    experience = models.PositiveSmallIntegerField('Опыт, лет', validators=[MaxValueValidator(70)])
    racing_class = models.CharField('Класс', max_length=6, choices=CLASSES)

    class Meta:
        ordering = ['full_name', 'pk']
        verbose_name = 'гонщик'
        verbose_name_plural = 'гонщики'

    def __str__(self):
        return self.full_name


class Race(models.Model):
    STATUSES = [('open', 'Регистрация открыта'), ('scheduled', 'Скоро старт'), ('finished', 'Завершена')]
    title = models.CharField('Название', max_length=150)
    slug = models.SlugField(unique=True)
    track = models.CharField('Трасса', max_length=100)
    location = models.CharField('Место проведения', max_length=150)
    start_date = models.DateField('Начало')
    end_date = models.DateField('Окончание')
    round_number = models.PositiveSmallIntegerField('Этап', validators=[MinValueValidator(1)])
    length_km = models.DecimalField('Длина круга, км', max_digits=5, decimal_places=3, validators=[MinValueValidator(0.001)])
    corners = models.PositiveSmallIntegerField('Поворотов', validators=[MinValueValidator(1)])
    capacity = models.PositiveSmallIntegerField('Максимум участников', default=30, validators=[MinValueValidator(1)])
    description = models.TextField('Описание')
    status = models.CharField('Статус', max_length=12, choices=STATUSES, default='open')
    image = models.CharField('Локальное изображение', max_length=80, choices=[
        ('race-orange.webp', 'Оранжевый GT3'), ('race-yellow.webp', 'Жёлтый GT3'), ('race-blue.webp', 'Гоночный пелотон')], default='race-orange.webp')

    class Meta:
        ordering = ['start_date', 'pk']
        verbose_name = 'гонка'
        verbose_name_plural = 'гонки'
        constraints = [models.CheckConstraint(check=models.Q(end_date__gte=models.F('start_date')), name='race_date_order')]

    @property
    def accepts_entries(self):
        return self.status == 'open' and self.start_date >= timezone.localdate()

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'Окончание не может быть раньше начала.'})

    def __str__(self):
        return self.title


class Entry(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='entries', verbose_name='Гонка')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='entries', verbose_name='Гонщик')
    number = models.PositiveSmallIntegerField('Стартовый номер', validators=[MinValueValidator(1), MaxValueValidator(999)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['number', 'pk']
        verbose_name = 'заявка'
        verbose_name_plural = 'заявки'
        constraints = [
            models.UniqueConstraint(fields=['race', 'driver'], name='unique_race_driver'),
            models.UniqueConstraint(fields=['race', 'number'], name='unique_race_number'),
            models.CheckConstraint(check=models.Q(number__gte=1, number__lte=999), name='valid_car_number'),
        ]

    def __str__(self):
        return f'#{self.number} · {self.driver} · {self.race}'


class Heat(models.Model):
    STATUSES = [('finished', 'Финиш'), ('dnf', 'Не финишировал'), ('dsq', 'Дисквалификация')]
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='heats', verbose_name='Участник')
    attempt = models.PositiveSmallIntegerField('Заезд №', default=1, validators=[MinValueValidator(1)])
    started_at = models.DateTimeField('Дата и время заезда')
    duration = models.DurationField('Время заезда', null=True, blank=True, help_text='ЧЧ:ММ:СС.ммм, например 00:01:42.385')
    position = models.PositiveSmallIntegerField('Место', null=True, blank=True, validators=[MinValueValidator(1)])
    status = models.CharField('Результат', max_length=10, choices=STATUSES, default='finished')
    note = models.CharField('Примечание судьи', max_length=250, blank=True)

    class Meta:
        ordering = ['attempt', 'position', 'duration', 'pk']
        verbose_name = 'заезд'
        verbose_name_plural = 'заезды'
        constraints = [
            models.UniqueConstraint(fields=['entry', 'attempt'], name='unique_entry_attempt'),
            models.CheckConstraint(check=models.Q(duration__isnull=True) | models.Q(duration__gt=timezone.timedelta()), name='positive_heat_time'),
            models.CheckConstraint(check=~models.Q(status='finished') | (models.Q(duration__isnull=False) & models.Q(position__isnull=False)), name='finished_has_result'),
        ]

    def clean(self):
        errors = {}
        if self.status == 'finished' and (self.duration is None or self.position is None):
            errors['duration'] = 'Для финиша укажите время и место.'
        if self.duration is not None and self.duration.total_seconds() <= 0:
            errors['duration'] = 'Время должно быть положительным.'
        if self.status != 'finished' and self.position is not None:
            errors['position'] = 'Для DNF / DSQ место не назначается.'
        if self.entry_id and self.started_at:
            day = timezone.localtime(self.started_at).date() if timezone.is_aware(self.started_at) else self.started_at.date()
            if not self.entry.race.start_date <= day <= self.entry.race.end_date:
                errors['started_at'] = 'Дата заезда должна входить в период гонки.'
        if self.entry_id and self.position and self.attempt:
            duplicate = Heat.objects.filter(entry__race=self.entry.race, attempt=self.attempt, position=self.position).exclude(pk=self.pk)
            if duplicate.exists():
                errors['position'] = 'Это место в данном заезде уже занято.'
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.entry} · заезд {self.attempt}'


class Comment(models.Model):
    TYPES = [('cooperation', 'Сотрудничество'), ('racing', 'Вопрос о гонках'), ('other', 'Иное')]
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='comments', verbose_name='Гонка')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='race_comments', verbose_name='Автор')
    date_from = models.DateField('Заезд: с')
    date_to = models.DateField('Заезд: по')
    text = models.TextField('Комментарий', max_length=2500)
    kind = models.CharField('Тип комментария', max_length=12, choices=TYPES)
    rating = models.PositiveSmallIntegerField('Оценка', validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-pk']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1, rating__lte=10), name='rating_1_to_10'),
            models.CheckConstraint(check=models.Q(date_to__gte=models.F('date_from')), name='comment_date_order'),
        ]

    def clean(self):
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValidationError({'date_to': 'Окончание периода раньше начала.'})
        if self.race_id and self.date_from and self.date_to:
            if self.date_from < self.race.start_date or self.date_to > self.race.end_date:
                raise ValidationError({'date_from': 'Даты должны входить в период гонки.'})

    def __str__(self):
        return f'{self.author} → {self.race} ({self.rating}/10)'
