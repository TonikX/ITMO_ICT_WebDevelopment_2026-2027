from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Country(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "страна"
        verbose_name_plural = "страны"

    def __str__(self):
        return self.name


class Agency(models.Model):
    name = models.CharField("Название", max_length=150)
    phone = models.CharField("Телефон", max_length=30)
    email = models.EmailField("Почта")

    class Meta:
        ordering = ["name"]
        verbose_name = "турагентство"
        verbose_name_plural = "турагентства"

    def __str__(self):
        return self.name


class Tour(models.Model):
    title = models.CharField("Название", max_length=200)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name="Страна")
    agency = models.ForeignKey(Agency, on_delete=models.PROTECT, verbose_name="Турагентство")
    description = models.TextField("Описание")
    start_date = models.DateField("Начало тура")
    end_date = models.DateField("Окончание тура")
    payment_terms = models.TextField("Условия оплаты")
    price = models.DecimalField("Цена за человека, ₽", max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["start_date", "pk"]
        verbose_name = "тур"
        verbose_name_plural = "туры"
        constraints = [
            models.CheckConstraint(condition=models.Q(end_date__gte=models.F("start_date")),
                                   name="tour_dates_order"),
            models.CheckConstraint(condition=models.Q(price__gte=1), name="tour_positive_price"),
        ]

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "Окончание тура не может быть раньше начала."})

    def __str__(self):
        return self.title


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает подтверждения"
        CONFIRMED = "confirmed", "Подтверждено"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             verbose_name="Пользователь")
    tour = models.ForeignKey(Tour, on_delete=models.PROTECT, related_name="bookings",
                             verbose_name="Тур")
    travelers = models.PositiveSmallIntegerField("Количество туристов", default=1,
                                                validators=[MinValueValidator(1), MaxValueValidator(20)])
    phone = models.CharField("Телефон для связи", max_length=30)
    comment = models.TextField("Пожелания", blank=True)
    unit_price = models.DecimalField("Цена за человека при бронировании", max_digits=10,
                                     decimal_places=2, validators=[MinValueValidator(1)])
    status = models.CharField("Статус", max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField("Дата бронирования", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "бронирование"
        verbose_name_plural = "бронирования"
        constraints = [
            models.UniqueConstraint(fields=["user", "tour"], name="unique_user_tour_booking"),
            models.CheckConstraint(condition=models.Q(travelers__gte=1, travelers__lte=20),
                                   name="booking_travelers_range"),
            models.CheckConstraint(condition=models.Q(unit_price__gte=1), name="booking_positive_price"),
            models.CheckConstraint(condition=models.Q(status__in=["pending", "confirmed"]),
                                   name="booking_valid_status"),
        ]

    @property
    def total_price(self):
        return self.unit_price * self.travelers

    def __str__(self):
        return f"{self.user} — {self.tour}"


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             verbose_name="Автор")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="reviews", verbose_name="Тур")
    start_date = models.DateField("Начало тура")
    end_date = models.DateField("Окончание тура")
    text = models.TextField("Отзыв")
    rating = models.PositiveSmallIntegerField("Оценка", validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField("Дата отзыва", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"
        constraints = [
            models.CheckConstraint(condition=models.Q(rating__gte=1, rating__lte=10),
                                   name="review_rating_range"),
            models.CheckConstraint(condition=models.Q(end_date__gte=models.F("start_date")),
                                   name="review_dates_order"),
        ]

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "Окончание тура не может быть раньше начала."})

    def __str__(self):
        return f"{self.user}: {self.rating}/10 — {self.tour}"
