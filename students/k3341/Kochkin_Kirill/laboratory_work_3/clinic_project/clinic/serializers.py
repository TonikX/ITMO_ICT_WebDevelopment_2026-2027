from rest_framework import serializers
from .models import (
    Patient, MedicalCard, Specialty, Doctor, Cabinet,
    DoctorSchedule, Appointment, Service,
    AppointmentService, Payment
)


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'


class MedicalCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalCard
        fields = '__all__'


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = '__all__'


class DoctorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = '__all__'


class DoctorSerializer(serializers.ModelSerializer):
    schedules = DoctorScheduleSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Doctor
        fields = '__all__'


class CabinetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cabinet
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class AppointmentServiceSerializer(serializers.ModelSerializer):
    service_info = ServiceSerializer(
        source='service',
        read_only=True
    )

    class Meta:
        model = AppointmentService
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    appointment_services = AppointmentServiceSerializer(
        many=True,
        read_only=True
    )

    services_detail = ServiceSerializer(
        source='services',
        many=True,
        read_only=True
    )

    class Meta:
        model = Appointment
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'