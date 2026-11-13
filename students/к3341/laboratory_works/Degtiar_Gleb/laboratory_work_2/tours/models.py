from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

class Country(models.Model):
    name = models.CharField('Страна', max_length=100, unique=True)
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Страны'
    def __str__(self): return self.name

class Agency(models.Model):
    name = models.CharField('Турагентство', max_length=150, unique=True)
    email = models.EmailField('Email', blank=True)
    def __str__(self): return self.name
    class Meta: verbose_name_plural = 'Турагентства'

class Tour(models.Model):
    title = models.CharField('Название', max_length=160)
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT, verbose_name='Турагентство')
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name='Страна')
    description = models.TextField('Описание')
    start_date = models.DateField('Начало тура')
    end_date = models.DateField('Окончание тура')
    payment_terms = models.TextField('Условия оплаты')
    price = models.DecimalField('Цена за человека, ₽', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField('Доступен для бронирования', default=True)
    class Meta:
        ordering = ['start_date', 'pk']
        verbose_name_plural = 'Туры'
        constraints = [models.CheckConstraint(check=models.Q(end_date__gte=models.F('start_date')), name='tour_dates_valid'),
                       models.CheckConstraint(check=models.Q(price__gte=0), name='tour_price_nonnegative')]
    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date':'Окончание не может быть раньше начала.'})
    def __str__(self): return self.title

class Booking(models.Model):
    PENDING, CONFIRMED = 'pending', 'confirmed'
    STATUS = [(PENDING,'Ожидает подтверждения'), (CONFIRMED,'Подтверждено')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    tour = models.ForeignKey(Tour, on_delete=models.PROTECT, verbose_name='Тур')
    travelers = models.PositiveSmallIntegerField('Число туристов', default=1, validators=[MinValueValidator(1),MaxValueValidator(20)])
    comment = models.TextField('Пожелания', blank=True, max_length=2000)
    status = models.CharField('Статус', max_length=12, choices=STATUS, default=PENDING)
    unit_price = models.DecimalField('Цена на момент бронирования', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    class Meta:
        ordering = ['-created_at','-pk']
        verbose_name_plural = 'Бронирования'
        constraints = [models.UniqueConstraint(fields=['user','tour'], name='one_booking_per_tour'),
          models.CheckConstraint(check=models.Q(travelers__gte=1, travelers__lte=20), name='booking_travelers_valid'),
          models.CheckConstraint(check=models.Q(unit_price__gte=0), name='booking_price_valid'),
          models.CheckConstraint(check=models.Q(status__in=['pending','confirmed']), name='booking_status_valid')]
    @property
    def total(self): return self.unit_price * self.travelers
    def __str__(self): return f'{self.user} — {self.tour}'

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, verbose_name='Тур')
    start_date = models.DateField('Дата начала тура')
    end_date = models.DateField('Дата окончания тура')
    text = models.TextField('Отзыв', max_length=3000)
    rating = models.PositiveSmallIntegerField('Оценка (1–10)', validators=[MinValueValidator(1),MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at','-pk']
        verbose_name_plural = 'Отзывы'
        constraints = [models.UniqueConstraint(fields=['user','tour'], name='one_review_per_tour'),
          models.CheckConstraint(check=models.Q(rating__gte=1,rating__lte=10), name='review_rating_valid'),
          models.CheckConstraint(check=models.Q(end_date__gte=models.F('start_date')), name='review_dates_valid')]
    def __str__(self): return f'{self.tour}: {self.rating}/10'
