from django.shortcuts import render
from rest_framework import viewsets

from .models import (
    Patient, MedicalCard, Specialty, Doctor, Cabinet,
    DoctorSchedule, Appointment, Service,
    AppointmentService, Payment
)

from .serializers import (
    PatientSerializer, MedicalCardSerializer,
    SpecialtySerializer, DoctorSerializer,
    CabinetSerializer, DoctorScheduleSerializer,
    AppointmentSerializer, ServiceSerializer,
    AppointmentServiceSerializer, PaymentSerializer
)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class MedicalCardViewSet(viewsets.ModelViewSet):
    queryset = MedicalCard.objects.all()
    serializer_class = MedicalCardSerializer


class SpecialtyViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all().prefetch_related('schedules')
    serializer_class = DoctorSerializer


class CabinetViewSet(viewsets.ModelViewSet):
    queryset = Cabinet.objects.all()
    serializer_class = CabinetSerializer


class DoctorScheduleViewSet(viewsets.ModelViewSet):
    queryset = DoctorSchedule.objects.all()
    serializer_class = DoctorScheduleSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().prefetch_related(
        'appointment_services__service',
        'services'
    )
    serializer_class = AppointmentSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class AppointmentServiceViewSet(viewsets.ModelViewSet):
    queryset = AppointmentService.objects.all()
    serializer_class = AppointmentServiceSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
