from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Расширенная модель пользователя"""
    passport_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Номер паспорта"
    )
    home_address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Домашний адрес"
    )
    nationality = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Национальность"
    )

    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"


class CarOwner(models.Model):
    """Модель владельца автомобиля"""
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    birth_date = models.DateField(verbose_name="Дата рождения", null=True, blank=True)
    passport_number = models.CharField(max_length=10, verbose_name="Номер паспорта", unique=True)
    address = models.TextField(verbose_name="Адрес", blank=True, null=True)

    cars = models.ManyToManyField('Car', through='Ownership', verbose_name="Автомобили")

    class Meta:
        verbose_name = "Владелец"
        verbose_name_plural = "Владельцы"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Car(models.Model):
    """Модель автомобиля"""
    BRAND_CHOICES = [
        ('BMW', 'BMW'),
        ('Mercedes', 'Mercedes-Benz'),
        ('Audi', 'Audi'),
        ('Toyota', 'Toyota'),
        ('Honda', 'Honda'),
        ('Ford', 'Ford'),
        ('Volkswagen', 'Volkswagen'),
        ('Nissan', 'Nissan'),
        ('Hyundai', 'Hyundai'),
        ('Kia', 'Kia'),
    ]

    COLOR_CHOICES = [
        ('black', 'Чёрный'),
        ('white', 'Белый'),
        ('red', 'Красный'),
        ('blue', 'Синий'),
        ('silver', 'Серебристый'),
        ('gray', 'Серый'),
    ]

    license_plate = models.CharField(max_length=10, verbose_name="Номер автомобиля", unique=True)
    brand = models.CharField(max_length=20, choices=BRAND_CHOICES, verbose_name="Марка")
    model = models.CharField(max_length=50, verbose_name="Модель")
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, verbose_name="Цвет")
    year = models.IntegerField(verbose_name="Год выпуска")

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.license_plate})"


class Ownership(models.Model):
    """Промежуточная модель владения автомобилем"""
    car_owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE, verbose_name="Владелец")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")
    start_date = models.DateField(verbose_name="Дата начала владения")
    end_date = models.DateField(verbose_name="Дата окончания владения", null=True, blank=True)

    class Meta:
        verbose_name = "Владение"
        verbose_name_plural = "Владения"
        unique_together = ['car_owner', 'car']

    def __str__(self):
        return f"{self.car_owner} владеет {self.car} с {self.start_date}"


class Racer(models.Model):
    """Модель гонщика"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name='racer_profile'
    )
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    team_name = models.CharField(max_length=100, verbose_name="Название команды")
    car_description = models.TextField(verbose_name="Описание автомобиля")
    experience = models.IntegerField(verbose_name="Опыт (лет)", default=0)
    racer_class = models.CharField(max_length=50, verbose_name="Класс участника")

    class Meta:
        verbose_name = "Гонщик"
        verbose_name_plural = "Гонщики"

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.team_name})"


class Race(models.Model):
    """Модель гонки"""
    name = models.CharField(max_length=200, verbose_name="Название гонки")
    race_date = models.DateTimeField(verbose_name="Дата и время гонки")
    track_location = models.CharField(max_length=200, verbose_name="Место проведения")
    description = models.TextField(verbose_name="Описание гонки", blank=True)
    racers = models.ManyToManyField(
        Racer,
        through='RaceRegistration',
        verbose_name="Участники",
        related_name='races'
    )

    class Meta:
        verbose_name = "Гонка"
        verbose_name_plural = "Гонки"
        ordering = ['-race_date']

    def __str__(self):
        return f"{self.name} ({self.race_date.strftime('%d.%m.%Y')})"


class RaceRegistration(models.Model):
    """Промежуточная модель регистрации на гонку"""
    racer = models.ForeignKey(
        Racer,
        on_delete=models.CASCADE,
        verbose_name="Гонщик",
        related_name='registrations'
    )
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        verbose_name="Гонка",
        related_name='registrations'
    )
    registration_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации"
    )

    race_time = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Время заезда"
    )
    result = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Место (результат)"
    )

    class Meta:
        verbose_name = "Регистрация на гонку"
        verbose_name_plural = "Регистрации на гонки"
        unique_together = ['racer', 'race']

    def __str__(self):
        return f"{self.racer} - {self.race}"


class Review(models.Model):
    """Модель отзыва к гонке"""
    COMMENT_TYPES = [
        ('cooperation', 'Вопрос о сотрудничестве'),
        ('race', 'Вопрос о гонках'),
        ('other', 'Иное'),
    ]

    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        verbose_name="Гонка",
        related_name='reviews'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор отзыва",
        related_name='reviews'
    )
    comment_text = models.TextField(verbose_name="Текст комментария")
    comment_type = models.CharField(
        max_length=20,
        choices=COMMENT_TYPES,
        verbose_name="Тип комментария"
    )
    rating = models.IntegerField(
        verbose_name="Рейтинг (1-10)",
        help_text="Оцените от 1 до 10"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв {self.author.username} к {self.race.name}"
