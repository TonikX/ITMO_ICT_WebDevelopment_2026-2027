from django.conf import settings
from django.db import models


class Doctor(models.Model):
    """
    Doctor

    Clinic doctor with employment and specialty data.
    """

    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctor_profile",
    )
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    specialty = models.CharField(max_length=150)
    education = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    birth_date = models.DateField()
    work_start = models.DateField()
    work_end = models.DateField(null=True, blank=True)
    contract_number = models.CharField(max_length=50)
    contract_date = models.DateField()

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(part for part in parts if part)


class DoctorSchedule(models.Model):
    """
    DoctorSchedule

    Working / day-off mark for a weekday.
    """

    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Понедельник"
        TUESDAY = 1, "Вторник"
        WEDNESDAY = 2, "Среда"
        THURSDAY = 3, "Четверг"
        FRIDAY = 4, "Пятница"
        SATURDAY = 5, "Суббота"
        SUNDAY = 6, "Воскресенье"

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    weekday = models.IntegerField(choices=Weekday.choices)
    is_working = models.BooleanField(default=True)

    class Meta:
        unique_together = ("doctor", "weekday")
        ordering = ["weekday"]

    def __str__(self) -> str:
        return f"{self.doctor} — {self.get_weekday_display()}"


class Cabinet(models.Model):
    """
    Cabinet

    Exam room with schedule and responsible doctor.
    """

    number = models.CharField(max_length=20, unique=True)
    work_start = models.TimeField()
    work_end = models.TimeField()
    responsible = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cabinets",
    )
    phone = models.CharField(max_length=30)

    class Meta:
        ordering = ["number"]

    def __str__(self) -> str:
        return f"Cabinet {self.number}"


class Service(models.Model):
    """
    Service

    Clinic price-list item.
    """

    name = models.CharField(max_length=200)
    specialty = models.CharField(max_length=150, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.price})"


class Patient(models.Model):
    """
    Patient

    Medical card holder (personal data + contact).
    """

    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_profile",
    )
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)
    phone = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    passport = models.CharField(max_length=20, unique=True)
    card_number = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(part for part in parts if part)


class Appointment(models.Model):
    """
    Appointment

    Paid commercial visit with diagnosis and recommendations.
    """

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    cabinet = models.ForeignKey(
        Cabinet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    visited_at = models.DateTimeField()
    diagnosis = models.CharField(max_length=255, blank=True)
    condition = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ["-visited_at"]

    def __str__(self) -> str:
        return f"{self.patient} / {self.doctor} @ {self.visited_at}"
