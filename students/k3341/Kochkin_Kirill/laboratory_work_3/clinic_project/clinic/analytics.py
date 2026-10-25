
from decimal import Decimal
from django.db.models import Prefetch
from django.db.models import Count, F, Sum, Value, DecimalField
from django.db.models.functions import Coalesce, TruncDate
from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Patient, Doctor, Appointment, AppointmentService


MONEY = DecimalField(max_digits=14, decimal_places=2)


# 1. Пациенты заданного врача
@api_view(['GET'])
def doctor_patients(request):
    doctor_id = request.query_params.get('doctor_id')

    if not doctor_id or not doctor_id.isdigit():
        return Response(
            {"error": "Укажите doctor_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    appointments = (
        Appointment.objects
        .filter(doctor_id=doctor_id)
        .select_related('medical_card__patient')
        .annotate(
            total=Coalesce(
                Sum(
                    F('appointment_services__quantity') *
                    F('appointment_services__price_at_appointment'),
                    output_field=MONEY
                ),
                Value(Decimal('0.00'), output_field=MONEY)
            )
        )
        .order_by(
            'medical_card__patient__last_name',
            'medical_card__patient__first_name',
            'date_time'
        )
    )

    result = [
        {
            "patient": str(a.medical_card.patient),
            "date": a.date_time.date(),
            "cost": str(a.total)
        }
        for a in appointments
    ]

    return Response(result)


# 2. Телефоны пациентов отоларинголога
@api_view(['GET'])
def ent_patients(request):
    patients = (
        Patient.objects
        .filter(
            birth_date__year__gt=1987,
            medical_card__appointments__doctor__specialty__name__iexact=
            'Отоларинголог'
        )
        .distinct()
        .order_by('last_name', 'first_name')
    )

    return Response([
        {
            "patient": str(p),
            "birth_date": p.birth_date,
            "phone": p.phone
        }
        for p in patients
    ])


# 3. Врачи, работающие в заданный день
@api_view(['GET'])
def working_doctors(request):
    raw_date = request.query_params.get('date', '')

    try:
        date = parse_date(raw_date)
    except ValueError:
        date = None

    if date is None:
        return Response(
            {"error": "Укажите дату в формате YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST
        )

    doctors = (
        Doctor.objects
        .filter(
            schedules__date=date,
            schedules__is_working_day=True
        )
        .select_related('specialty')
        .order_by('last_name', 'first_name')
    )

    return Response([
        {
            "doctor": str(d),
            "specialty": d.specialty.name
        }
        for d in doctors
    ])


# 4. Количество приёмов по датам
@api_view(['GET'])
def appointments_by_date(request):
    result = (
        Appointment.objects
        .annotate(day=TruncDate('date_time'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    return Response(list(result))


# 5. Стоимость лечения по дням и врачам
@api_view(['GET'])
def treatment_costs(request):
    result = (
        AppointmentService.objects
        .annotate(day=TruncDate('appointment__date_time'))
        .values(
            'day',
            'appointment__doctor_id',
            'appointment__doctor__last_name',
            'appointment__doctor__first_name'
        )
        .annotate(
            total=Sum(
                F('quantity') * F('price_at_appointment'),
                output_field=MONEY
            )
        )
        .order_by('day', 'appointment__doctor__last_name')
    )

    return Response([
        {
            "date": row['day'],
            "doctor_id": row['appointment__doctor_id'],
            "doctor": (
                row['appointment__doctor__last_name'] + ' ' +
                row['appointment__doctor__first_name']
            ),
            "total": str(row['total'])
        }
        for row in result
    ])


# 6. Пациенты, оплатившие лечение
@api_view(['GET'])
def paid_patients(request):
    patients = (
        Patient.objects
        .filter(
            medical_card__appointments__payment__isnull=False
        )
        .distinct()
        .order_by('last_name', 'first_name')
    )

    return Response([
        {
            "id": p.id,
            "patient": str(p),
            "phone": p.phone
        }
        for p in patients
    ])

# 7. Отчёт о работе врачей за период
@api_view(['GET'])
def doctors_report(request):
    start_raw = request.query_params.get('start_date', '')
    end_raw = request.query_params.get('end_date', '')

    try:
        start_date = parse_date(start_raw)
        end_date = parse_date(end_raw)
    except ValueError:
        start_date = end_date = None

    if not start_date or not end_date:
        return Response(
            {"error": "Укажите start_date и end_date в формате YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if start_date > end_date:
        return Response(
            {"error": "Начальная дата не может быть позже конечной"},
            status=status.HTTP_400_BAD_REQUEST
        )

    appointments = (
        Appointment.objects
        .filter(date_time__date__range=(start_date, end_date))
        .select_related('medical_card__patient', 'payment')
        .prefetch_related('appointment_services__service')
        .order_by('date_time')
    )

    doctors = (
        Doctor.objects
        .select_related('specialty')
        .prefetch_related(
            Prefetch(
                'appointments',
                queryset=appointments,
                to_attr='period_appointments'
            )
        )
        .order_by('last_name', 'first_name')
    )

    result = []
    clinic_income = Decimal('0.00')

    for doctor in doctors:
        doctor_income = Decimal('0.00')
        accepted_patients = []

        for appointment in doctor.period_appointments:
            services = []
            total_cost = Decimal('0.00')

            for item in appointment.appointment_services.all():
                cost = item.quantity * item.price_at_appointment
                total_cost += cost

                services.append({
                    "name": item.service.name,
                    "quantity": item.quantity,
                    "price": str(item.price_at_appointment),
                    "cost": str(cost)
                })

            payment = getattr(appointment, 'payment', None)
            is_paid = payment is not None

            if is_paid:
                doctor_income += payment.amount

            accepted_patients.append({
                "patient": str(appointment.medical_card.patient),
                "date": appointment.date_time,
                "diagnosis": appointment.diagnosis,
                "services": services,
                "total_cost": str(total_cost),
                "is_paid": is_paid
            })

        clinic_income += doctor_income

        result.append({
            "doctor": str(doctor),
            "specialty": doctor.specialty.name,
            "appointments_count": len(accepted_patients),
            "patients": accepted_patients,
            "total_income": str(doctor_income)
        })

    return Response({
        "start_date": start_date,
        "end_date": end_date,
        "doctors": result,
        "clinic_income": str(clinic_income)
    })