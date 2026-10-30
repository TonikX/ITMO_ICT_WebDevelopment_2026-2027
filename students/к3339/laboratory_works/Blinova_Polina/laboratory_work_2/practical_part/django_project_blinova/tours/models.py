from django.conf import settings
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator


class Country(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    code = models.CharField('Код', max_length=3, unique=True)

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'
        ordering = ['name']

    def __str__(self):
        return self.name


class TourAgency(models.Model):
    name = models.CharField('Название', max_length=200)
    address = models.CharField('Адрес', max_length=255)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Турагентство'
        verbose_name_plural = 'Турагентства'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tour(models.Model):
    PAYMENT_CHOICES = [
        ('full', 'Полная предоплата'),
        ('half', '50% предоплата'),
        ('installment', 'Рассрочка'),
        ('post', 'Оплата по факту'),
    ]

    name = models.CharField('Название тура', max_length=200)
    agency = models.ForeignKey(
        TourAgency, on_delete=models.CASCADE,
        related_name='tours', verbose_name='Турагентство'
    )
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT,
        related_name='tours', verbose_name='Страна'
    )
    description = models.TextField('Описание тура')
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    payment_terms = models.CharField(
        'Условия оплаты', max_length=20,
        choices=PAYMENT_CHOICES, default='full'
    )
    max_participants = models.PositiveIntegerField('Максимум участников', default=20)
    image = models.ImageField('Изображение', upload_to='tours/', blank=True, null=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Тур'
        verbose_name_plural = 'Туры'
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.name} ({self.country})'

    def get_absolute_url(self):
        return reverse('tour_detail', kwargs={'pk': self.pk})

    @property
    def sold_count(self):
        return self.reservations.filter(status='confirmed').count()

    @property
    def available_slots(self):
        return self.max_participants - self.sold_count


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reservations', verbose_name='Пользователь'
    )
    tour = models.ForeignKey(
        Tour, on_delete=models.CASCADE,
        related_name='reservations', verbose_name='Тур'
    )
    participants_count = models.PositiveIntegerField('Количество участников', default=1)
    status = models.CharField(
        'Статус', max_length=20,
        choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Резервирование'
        verbose_name_plural = 'Резервирования'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.tour.name} ({self.get_status_display()})'

    @property
    def total_price(self):
        return self.tour.price * self.participants_count


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Пользователь'
    )
    tour = models.ForeignKey(
        Tour, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Тур'
    )
    text = models.TextField('Текст отзыва')
    rating = models.PositiveSmallIntegerField(
        'Рейтинг', validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = ('user', 'tour')

    def __str__(self):
        return f'{self.user.username} → {self.tour.name}: {self.rating}/10'