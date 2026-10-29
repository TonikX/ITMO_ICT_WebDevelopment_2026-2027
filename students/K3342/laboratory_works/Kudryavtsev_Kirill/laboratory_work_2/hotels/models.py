from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Hotel(models.Model):
    name = models.CharField('Название', max_length=120)
    owner = models.CharField('Владелец', max_length=120)
    city = models.CharField('Город', max_length=80)
    address = models.CharField('Адрес', max_length=200)
    description = models.TextField('Описание')

    class Meta:
        ordering = ['name', 'pk']
        verbose_name = 'отель'
        verbose_name_plural = 'отели'

    def __str__(self):
        return self.name


class Room(models.Model):
    TYPES = [('single', 'Одноместный'), ('double', 'Двухместный'), ('family', 'Семейный'), ('suite', 'Люкс')]
    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT, related_name='rooms', verbose_name='Отель')
    number = models.CharField('Номер комнаты', max_length=10)
    room_type = models.CharField('Тип номера', max_length=10, choices=TYPES)
    price = models.DecimalField('Стоимость за ночь, ₽', max_digits=9, decimal_places=2, validators=[MinValueValidator(1)])
    capacity = models.PositiveSmallIntegerField('Вместимость', validators=[MinValueValidator(1)])
    amenities = models.TextField('Удобства')

    class Meta:
        ordering = ['hotel__name', 'number', 'pk']
        unique_together = [('hotel', 'number')]
        constraints = [models.CheckConstraint(check=Q(price__gt=0) & Q(capacity__gt=0), name='room_positive_values')]
        verbose_name = 'номер'
        verbose_name_plural = 'номера'

    def __str__(self):
        return f'{self.hotel.name}, №{self.number}'


class Booking(models.Model):
    BOOKED, IN, OUT = 'booked', 'in', 'out'
    STATUS = [(BOOKED, 'Забронировано'), (IN, 'Заселён'), (OUT, 'Выселен')]
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='bookings', verbose_name='Номер')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Гость')
    arrival = models.DateField('Дата заезда')
    departure = models.DateField('Дата выезда')
    guests = models.PositiveSmallIntegerField('Число гостей', default=1, validators=[MinValueValidator(1)])
    status = models.CharField('Статус', max_length=10, choices=STATUS, default=BOOKED)
    checked_in_at = models.DateTimeField('Фактическое заселение', null=True, blank=True)
    checked_out_at = models.DateTimeField('Фактическое выселение', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-arrival', '-pk']
        constraints = [
            models.CheckConstraint(check=Q(departure__gt=F('arrival')), name='booking_ordered_dates'),
            models.CheckConstraint(check=Q(guests__gt=0), name='booking_positive_guests'),
        ]
        verbose_name = 'бронирование'
        verbose_name_plural = 'бронирования'

    @property
    def total(self):
        return (self.departure - self.arrival).days * self.room.price

    def __str__(self):
        return f'{self.user} — {self.room} ({self.arrival} — {self.departure})'

    def clean(self):
        super().clean()
        if self.arrival and self.departure and self.arrival >= self.departure:
            raise ValidationError({'departure': 'Дата выезда должна быть позже даты заезда.'})
        if self.room_id and self.guests and self.guests > self.room.capacity:
            raise ValidationError({'guests': 'Число гостей превышает вместимость номера.'})
        if self.room_id and self.arrival and self.departure and self.status in [self.BOOKED, self.IN]:
            conflicts = Booking.objects.filter(room_id=self.room_id, status__in=[self.BOOKED, self.IN],
                arrival__lt=self.departure, departure__gt=self.arrival).exclude(pk=self.pk)
            if conflicts.exists():
                raise ValidationError('Номер занят на выбранные даты.')
        if self.status == self.BOOKED and (self.checked_in_at or self.checked_out_at):
            raise ValidationError('У бронирования не должно быть дат заселения и выселения.')
        if self.status == self.IN and (not self.checked_in_at or self.checked_out_at):
            raise ValidationError('Для заселённого гостя нужна только дата заселения.')
        if self.status == self.OUT and (not self.checked_in_at or not self.checked_out_at):
            raise ValidationError('Для выселенного гостя нужны обе фактические даты.')
        if self.checked_in_at and self.checked_out_at and self.checked_out_at < self.checked_in_at:
            raise ValidationError('Выселение не может предшествовать заселению.')

    def change_status(self, action):
        now = timezone.now()
        today = timezone.localdate()
        if action == 'checkin' and self.status == self.BOOKED:
            if not self.arrival <= today < self.departure:
                raise ValidationError('Заселение возможно только в период бронирования.')
            self.status, self.checked_in_at = self.IN, now
        elif action == 'checkout' and self.status == self.IN:
            self.status, self.checked_out_at = self.OUT, now
        else:
            raise ValidationError('Это действие недоступно для текущего статуса.')
        self.full_clean()
        self.save()


class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.PROTECT, related_name='review', verbose_name='Проживание')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='reviews', verbose_name='Номер')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Автор')
    arrival = models.DateField('Начало проживания')
    departure = models.DateField('Конец проживания')
    text = models.TextField('Отзыв', max_length=3000)
    rating = models.PositiveSmallIntegerField('Оценка', validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-pk']
        constraints = [models.CheckConstraint(check=Q(rating__gte=1) & Q(rating__lte=10), name='review_rating_range')]
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'

    def __str__(self):
        return f'{self.user}: {self.rating}/10'

    def clean(self):
        super().clean()
        if self.booking_id:
            b = self.booking
            if b.status != Booking.OUT or self.user_id != b.user_id or self.room_id != b.room_id:
                raise ValidationError('Отзыв доступен только о своём завершённом проживании.')
            if (self.arrival, self.departure) != (timezone.localtime(b.checked_in_at).date(), timezone.localtime(b.checked_out_at).date()):
                raise ValidationError('Даты отзыва должны соответствовать фактическому проживанию.')
