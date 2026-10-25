
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.utils import timezone

from clinic.models import (
    Patient, MedicalCard, Specialty, Doctor, Cabinet,
    DoctorSchedule, Appointment, Service,
    AppointmentService, Payment
)


# Специальности
specialties = {}

for name in ["Отоларинголог", "Терапевт", "Кардиолог"]:
    specialty, _ = Specialty.objects.get_or_create(name=name)
    specialties[name] = specialty


# Пациенты и медицинские карты
patients_data = [
    ("Сидоров", "Артём", "1994-07-12", "+79000000001"),
    ("Смирнова", "Ирина", "1983-04-03", "+79000000002"),
    ("Кузнецов", "Максим", "2002-01-22", "+79000000003"),
    ("Морозова", "Елена", "1978-10-30", "+79000000004"),
    ("Фёдоров", "Никита", "1991-11-17", "+79000000005"),
]

cards = {}

for i, (last, first, birth, phone) in enumerate(patients_data, 1):
    patient, _ = Patient.objects.get_or_create(
        phone=phone,
        defaults={
            "last_name": last,
            "first_name": first,
            "birth_date": date.fromisoformat(birth),
            "address": "Санкт-Петербург"
        }
    )

    card, _ = MedicalCard.objects.get_or_create(
        number=f"MC-DEMO-{i:03d}",
        defaults={
            "patient": patient,
            "created_at": date(2026, 10, 1)
        }
    )

    cards[last] = card


# Врачи
doctors_data = [
    ("Орлова", "Мария", "Отоларинголог"),
    ("Соколова", "Анна", "Терапевт"),
    ("Климов", "Дмитрий", "Кардиолог"),
]

doctors = {}

for last, first, specialty in doctors_data:
    doctor, _ = Doctor.objects.get_or_create(
        last_name=last,
        first_name=first,
        defaults={
            "specialty": specialties[specialty],
            "employment_start_date": date(2020, 9, 1),
            "education": "Высшее медицинское"
        }
    )

    doctors[last] = doctor


# Кабинеты
cabinets = {}

for number in ["201", "202"]:
    cabinet, _ = Cabinet.objects.get_or_create(
        number=number,
        defaults={
            "working_hours": "Пн-Пт 09:00-18:00",
            "responsible_person": "Администратор клиники",
            "internal_phone": number
        }
    )

    cabinets[number] = cabinet


# Графики врачей
schedule_data = {
    "Орлова": ["2026-10-19", "2026-10-20"],
    "Соколова": ["2026-10-20", "2026-10-21", "2026-10-22"],
    "Климов": ["2026-10-21", "2026-10-22"],
}

for doctor_name, days in schedule_data.items():
    for day in days:
        DoctorSchedule.objects.get_or_create(
            doctor=doctors[doctor_name],
            date=date.fromisoformat(day),
            defaults={
                "is_working_day": True,
                "start_time": time(9, 0),
                "end_time": time(18, 0),
                "break_start": time(13, 0),
                "break_end": time(14, 0)
            }
        )

# Один нерабочий день
DoctorSchedule.objects.get_or_create(
    doctor=doctors["Соколова"],
    date=date(2026, 10, 23),
    defaults={"is_working_day": False}
)


# Услуги
services_data = [
    ("Консультация отоларинголога", "2000.00"),
    ("Приём терапевта", "1500.00"),
    ("Приём кардиолога", "2500.00"),
    ("ЭКГ", "900.00"),
    ("Общий анализ крови", "700.00"),
]

services = {}

for name, price in services_data:
    service, _ = Service.objects.get_or_create(
        name=name,
        defaults={"price": Decimal(price)}
    )
    services[name] = service


# Приёмы: пациент, врач, кабинет, дата,
# оказанные услуги, способ оплаты (или None)
appointments_data = [
    (
        "Сидоров", "Орлова", "201", "2026-10-19T10:00:00",
        ["Консультация отоларинголога", "Общий анализ крови"],
        "Карта"
    ),
    (
        "Кузнецов", "Орлова", "201", "2026-10-20T11:00:00",
        ["Консультация отоларинголога"],
        None
    ),
    (
        "Морозова", "Соколова", "202", "2026-10-20T09:30:00",
        ["Приём терапевта", "ЭКГ"],
        "Наличные"
    ),
    (
        "Смирнова", "Климов", "201", "2026-10-21T10:00:00",
        ["Приём кардиолога", "ЭКГ"],
        "Карта"
    ),
    (
        "Фёдоров", "Соколова", "202", "2026-10-21T11:00:00",
        ["Приём терапевта"],
        None
    ),
    (
        "Сидоров", "Климов", "201", "2026-10-22T12:00:00",
        ["Приём кардиолога"],
        "Перевод"
    ),
    (
        "Кузнецов", "Соколова", "202", "2026-10-22T16:00:00",
        ["Приём терапевта", "Общий анализ крови"],
        None
    ),
]

for patient_name, doctor_name, cabinet_number, dt, service_names, payment_method in appointments_data:
    appointment_datetime = timezone.make_aware(
        datetime.fromisoformat(dt)
    )

    appointment, _ = Appointment.objects.get_or_create(
        medical_card=cards[patient_name],
        doctor=doctors[doctor_name],
        date_time=appointment_datetime,
        defaults={
            "cabinet": cabinets[cabinet_number],
            "diagnosis": "Первичный осмотр",
            "current_condition": "Стабильное",
            "recommendations": "Выполнять назначения врача"
        }
    )

    total = Decimal("0.00")

    for service_name in service_names:
        service = services[service_name]

        AppointmentService.objects.get_or_create(
            appointment=appointment,
            service=service,
            defaults={
                "quantity": 1,
                "price_at_appointment": service.price
            }
        )

        total += service.price

    if payment_method:
        Payment.objects.get_or_create(
            appointment=appointment,
            defaults={
                "amount": total,
                "date_time": appointment_datetime + timedelta(minutes=40),
                "payment_method": payment_method
            }
        )


print("Тестовые данные добавлены!")
print("Пациентов:", Patient.objects.count())
print("Врачей:", Doctor.objects.count())
print("Приёмов:", Appointment.objects.count())
print("Оплат:", Payment.objects.count())
