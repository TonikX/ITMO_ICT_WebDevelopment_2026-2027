from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_DOCTOR = "doctor"
    ROLE_PATIENT = "patient"
    ROLE_CHOICES = (
        (ROLE_ADMIN, "admin"),
        (ROLE_DOCTOR, "doctor"),
        (ROLE_PATIENT, "patient"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PATIENT)

    def __str__(self):
        return self.username


class Doctor(models.Model):
    GENDER_CHOICES = (("M", "M"), ("F", "F"))

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
        null=True,
        blank=True,
    )
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    specialty = models.CharField(max_length=120)
    education = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField()
    hire_date = models.DateField()
    fire_date = models.DateField(null=True, blank=True)
    contract_info = models.TextField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.specialty})"

    @property
    def fio(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)


class Patient(models.Model):
    GENDER_CHOICES = (("M", "M"), ("F", "F"))

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name="patient_profile",
        null=True,
        blank=True,
    )
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def fio(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join(p for p in parts if p)


class MedicalCard(models.Model):
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name="medical_card",
    )
    opened_at = models.DateField()

    def __str__(self):
        return f"Card #{self.pk} — {self.patient}"


class Cabinet(models.Model):
    number = models.CharField(max_length=20, unique=True)
    schedule = models.CharField(max_length=255, blank=True)
    responsible_doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cabinets",
    )
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"Cabinet {self.number}"


class PriceList(models.Model):
    service_name = models.CharField(max_length=200)
    specialty = models.CharField(max_length=120, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["service_name"]

    def __str__(self):
        return f"{self.service_name} — {self.price}"


class WorkSchedule(models.Model):
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    work_date = models.DateField()
    is_working = models.BooleanField(default=True)

    class Meta:
        ordering = ["work_date"]
        unique_together = ("doctor", "work_date")

    def __str__(self):
        status = "work" if self.is_working else "off"
        return f"{self.doctor} — {self.work_date} ({status})"


class Visit(models.Model):
    medical_card = models.ForeignKey(
        MedicalCard,
        on_delete=models.CASCADE,
        related_name="visits",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="visits",
    )
    cabinet = models.ForeignKey(
        Cabinet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visits",
    )
    price_list = models.ForeignKey(
        PriceList,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visits",
    )
    visit_at = models.DateTimeField()
    diagnosis = models.CharField(max_length=255)
    condition = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ["-visit_at"]

    def __str__(self):
        return f"Visit #{self.pk} — {self.medical_card.patient} / {self.doctor}"
