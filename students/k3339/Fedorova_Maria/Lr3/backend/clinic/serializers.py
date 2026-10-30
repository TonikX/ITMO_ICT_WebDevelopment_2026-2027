from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Appointment,
    Cabinet,
    Doctor,
    DoctorSchedule,
    Patient,
    Service,
)
from .permissions import get_doctor, get_patient


class UserSerializer(serializers.ModelSerializer):
    """
    UserSerializer

    Auth user payload with role flags for the React client.
    """

    is_doctor = serializers.SerializerMethodField()
    is_patient = serializers.SerializerMethodField()
    doctor_id = serializers.SerializerMethodField()
    patient_id = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "is_staff",
            "is_doctor",
            "is_patient",
            "doctor_id",
            "patient_id",
            "role",
        )

    def get_is_doctor(self, user) -> bool:
        return get_doctor(user) is not None

    def get_is_patient(self, user) -> bool:
        return get_patient(user) is not None

    def get_doctor_id(self, user) -> int | None:
        doctor = get_doctor(user)
        return doctor.id if doctor else None

    def get_patient_id(self, user) -> int | None:
        patient = get_patient(user)
        return patient.id if patient else None

    def get_role(self, user) -> str:
        if user.is_staff:
            return "admin"
        if get_doctor(user):
            return "doctor"
        if get_patient(user):
            return "patient"
        return "guest"


class DoctorScheduleSerializer(serializers.ModelSerializer):
    weekday_display = serializers.CharField(
        source="get_weekday_display",
        read_only=True,
    )

    class Meta:
        model = DoctorSchedule
        fields = (
            "id",
            "doctor",
            "weekday",
            "weekday_display",
            "is_working",
        )


class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    schedules = DoctorScheduleSerializer(many=True, read_only=True)
    username = serializers.CharField(
        source="user.username",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Doctor
        fields = (
            "id",
            "user",
            "username",
            "last_name",
            "first_name",
            "middle_name",
            "full_name",
            "specialty",
            "education",
            "gender",
            "birth_date",
            "work_start",
            "work_end",
            "contract_number",
            "contract_date",
            "schedules",
        )
        read_only_fields = ("user",)


class CabinetSerializer(serializers.ModelSerializer):
    responsible_name = serializers.CharField(
        source="responsible.full_name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Cabinet
        fields = (
            "id",
            "number",
            "work_start",
            "work_end",
            "responsible",
            "responsible_name",
            "phone",
        )


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "specialty",
            "price",
        )


class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    username = serializers.CharField(
        source="user.username",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Patient
        fields = (
            "id",
            "user",
            "username",
            "last_name",
            "first_name",
            "middle_name",
            "full_name",
            "birth_date",
            "gender",
            "phone",
            "address",
            "passport",
            "card_number",
        )
        read_only_fields = ("user",)


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(
        source="patient.full_name",
        read_only=True,
    )
    doctor_name = serializers.CharField(
        source="doctor.full_name",
        read_only=True,
    )
    service_name = serializers.CharField(
        source="service.name",
        read_only=True,
    )
    doctor_specialty = serializers.CharField(
        source="doctor.specialty",
        read_only=True,
    )

    class Meta:
        model = Appointment
        fields = (
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "doctor_specialty",
            "cabinet",
            "service",
            "service_name",
            "visited_at",
            "diagnosis",
            "condition",
            "recommendations",
            "cost",
            "is_paid",
        )
        read_only_fields = ("cost", "is_paid")
        extra_kwargs = {
            "doctor": {"required": False},
            "patient": {"required": False},
            "diagnosis": {"required": False, "allow_blank": True},
            "condition": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        service = validated_data["service"]
        validated_data["cost"] = service.price
        validated_data["is_paid"] = False
        return super().create(validated_data)

    def update(self, instance, validated_data):
        service = validated_data.get("service", instance.service)
        validated_data["cost"] = service.price
        validated_data.pop("is_paid", None)
        return super().update(instance, validated_data)
