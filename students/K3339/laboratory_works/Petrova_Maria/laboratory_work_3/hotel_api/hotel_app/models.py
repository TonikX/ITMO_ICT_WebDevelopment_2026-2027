from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q


class RoomType(models.Model):
    CAPACITIES = [(1, "Одноместный"), (2, "Двухместный"), (3, "Трёхместный")]

    name = models.CharField(max_length=30, unique=True)
    capacity = models.PositiveSmallIntegerField(choices=CAPACITIES, unique=True)
    price_per_night = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(capacity__in=[1, 2, 3]),
                name="room_type_capacity_valid",
            ),
            models.CheckConstraint(
                condition=Q(price_per_night__gt=0),
                name="room_type_price_positive",
            ),
        ]

    def __str__(self):
        return self.name


class Floor(models.Model):
    number = models.PositiveSmallIntegerField(unique=True, validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(number__gte=1), name="floor_number_positive"),
        ]

    def __str__(self):
        return f"Этаж {self.number}"


class Room(models.Model):
    number = models.CharField(max_length=10, unique=True)
    floor = models.ForeignKey(Floor, on_delete=models.PROTECT, related_name="rooms")
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, related_name="rooms")
    phone = models.CharField(max_length=30)

    def __str__(self):
        return f"Номер {self.number}"


class Guest(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    passport_series = models.CharField(max_length=10)
    passport_number = models.CharField(max_length=20)
    arrival_city = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["passport_series", "passport_number"], name="guest_passport_unique"
            ),
        ]

    def __str__(self):
        return " ".join(filter(None, [self.last_name, self.first_name, self.middle_name]))


class Accommodation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="accommodations")
    check_in = models.DateField()
    planned_check_out = models.DateField()
    actual_check_out = models.DateField(null=True, blank=True)
    price_per_night = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(planned_check_out__gt=F("check_in")),
                name="accommodation_planned_dates_valid",
            ),
            models.CheckConstraint(
                condition=Q(actual_check_out__isnull=True) | Q(actual_check_out__gt=F("check_in")),
                name="accommodation_actual_dates_valid",
            ),
            models.CheckConstraint(
                condition=Q(price_per_night__gt=0), name="accommodation_price_positive"
            ),
        ]

    def save(self, *args, **kwargs):
        # Снимок тарифа создаётся только при первом сохранении.
        if self._state.adding and self.price_per_night is None:
            self.price_per_night = self.room.room_type.price_per_night
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.room}, с {self.check_in}"


class Stay(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.PROTECT, related_name="stays")
    accommodation = models.ForeignKey(
        Accommodation, on_delete=models.PROTECT, related_name="stays"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["guest", "accommodation"], name="stay_guest_accommodation_unique"
            ),
        ]

    def __str__(self):
        return f"{self.guest} — {self.accommodation}"


class Employee(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    hired_on = models.DateField()
    dismissed_on = models.DateField(null=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="employee",
    )
    floors = models.ManyToManyField(
        Floor, through="CleaningSchedule", related_name="employees", blank=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(dismissed_on__isnull=True) | Q(dismissed_on__gte=F("hired_on")),
                name="employee_dates_valid",
            ),
        ]

    def __str__(self):
        return " ".join(filter(None, [self.last_name, self.first_name, self.middle_name]))


class CleaningSchedule(models.Model):
    WEEKDAYS = [
        (0, "Понедельник"), (1, "Вторник"), (2, "Среда"),
        (3, "Четверг"), (4, "Пятница"), (5, "Суббота"), (6, "Воскресенье"),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="cleaning_assignments"
    )
    floor = models.ForeignKey(
        Floor, on_delete=models.PROTECT, related_name="cleaning_assignments"
    )
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAYS)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(weekday__gte=0, weekday__lte=6), name="cleaning_weekday_valid"
            ),
            models.CheckConstraint(
                condition=Q(valid_to__isnull=True) | Q(valid_to__gt=F("valid_from")),
                name="cleaning_dates_valid",
            ),
            models.UniqueConstraint(
                fields=["employee", "floor", "weekday", "valid_from"],
                name="cleaning_assignment_unique",
            ),
        ]

    def __str__(self):
        return f"{self.employee} — {self.floor}, {self.get_weekday_display()}"
