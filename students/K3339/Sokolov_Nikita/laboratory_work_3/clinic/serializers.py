from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from rest_framework import serializers

from .models import (
    Cabinet,
    Doctor,
    MedicalCard,
    Patient,
    PriceList,
    Visit,
    WorkSchedule,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "first_name", "last_name")


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = ("id", "username", "email", "password", "role", "first_name", "last_name")


class DoctorSerializer(serializers.ModelSerializer):
    fio = serializers.CharField(read_only=True)

    class Meta:
        model = Doctor
        fields = "__all__"


class PatientSerializer(serializers.ModelSerializer):
    fio = serializers.CharField(read_only=True)

    class Meta:
        model = Patient
        fields = "__all__"


class MedicalCardSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source="patient",
        write_only=True,
    )

    class Meta:
        model = MedicalCard
        fields = ("id", "patient", "patient_id", "opened_at")


class VisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = "__all__"


class VisitNestedSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    cabinet = serializers.StringRelatedField(read_only=True)
    price_list = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Visit
        fields = (
            "id",
            "visit_at",
            "diagnosis",
            "condition",
            "recommendations",
            "cost",
            "is_paid",
            "doctor",
            "cabinet",
            "price_list",
        )


class MedicalCardWithVisitsSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    visits = VisitNestedSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalCard
        fields = ("id", "opened_at", "patient", "visits")


class DoctorWithPatientsSerializer(serializers.ModelSerializer):
    fio = serializers.CharField(read_only=True)
    patients = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = (
            "id",
            "fio",
            "specialty",
            "education",
            "gender",
            "birth_date",
            "hire_date",
            "fire_date",
            "contract_info",
            "patients",
        )

    def get_patients(self, obj):
        patients = (
            Patient.objects.filter(medical_card__visits__doctor=obj)
            .distinct()
            .order_by("last_name", "first_name")
        )
        return PatientSerializer(patients, many=True).data


class CabinetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cabinet
        fields = "__all__"


class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = "__all__"


class WorkScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSchedule
        fields = "__all__"
