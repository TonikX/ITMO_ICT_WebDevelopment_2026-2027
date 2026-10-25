
from django.db import models
from django.core.validators import MinValueValidator

class Patient(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class MedicalCard(models.Model):
    number = models.CharField(max_length=30, unique=True)
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_card'
    )
    created_at = models.DateField()

    def __str__(self):
        return f"Карта №{self.number}"


class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)

    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.PROTECT,
        related_name='doctors'
    )

    education = models.TextField(blank=True)
    gender = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    employment_start_date = models.DateField()
    employment_end_date = models.DateField(null=True, blank=True)

    contract_number = models.CharField(max_length=100, blank=True)
    contract_date = models.DateField(null=True, blank=True)
    contract_terms = models.TextField(blank=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Cabinet(models.Model):
    number = models.CharField(max_length=20, unique=True)
    working_hours = models.TextField()
    responsible_person = models.CharField(max_length=255)
    internal_phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Кабинет №{self.number}"


class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='schedules'
    )

    date = models.DateField()
    is_working_day = models.BooleanField()

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'date'],
                name='unique_doctor_schedule'
            )
        ]

    def __str__(self):
        return f"{self.doctor} — {self.date}"


class Appointment(models.Model):
    medical_card = models.ForeignKey(
        MedicalCard,
        on_delete=models.PROTECT,
        related_name='appointments'
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.PROTECT,
        related_name='appointments'
    )

    cabinet = models.ForeignKey(
        Cabinet,
        on_delete=models.PROTECT,
        related_name='appointments'
    )

    date_time = models.DateTimeField()
    diagnosis = models.TextField(blank=True)
    current_condition = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)

    services = models.ManyToManyField(
        'Service',
        through='AppointmentService',
        related_name='appointments',
        blank=True
    )

    def __str__(self):
        return f"Приём №{self.id} — {self.date_time}"


class Service(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return self.name


class AppointmentService(models.Model):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='appointment_services'
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='appointment_services'
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    price_at_appointment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['appointment', 'service'],
                name='unique_appointment_service'
            )
        ]

    def __str__(self):
        return f"{self.service} — приём №{self.appointment_id}"


class Payment(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    date_time = models.DateTimeField()
    payment_method = models.CharField(max_length=50)

    def __str__(self):
        return f"Оплата приёма №{self.appointment_id}"
