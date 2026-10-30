from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Appointment, Cabinet, Doctor, DoctorSchedule, Patient, Service
from .permissions import (
    IsStaffDoctorOrPatient,
    IsStaffOrDoctor,
    get_doctor,
    get_patient,
)
from .serializers import (
    AppointmentSerializer,
    CabinetSerializer,
    DoctorScheduleSerializer,
    DoctorSerializer,
    PatientSerializer,
    ServiceSerializer,
    UserSerializer,
)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class DoctorListCreateView(generics.ListCreateAPIView):
    serializer_class = DoctorSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["last_name", "first_name", "specialty"]
    ordering_fields = ["last_name", "specialty", "work_start"]
    ordering = ["last_name"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = Doctor.objects.prefetch_related("schedules").all()
        specialty = self.request.query_params.get("specialty")
        if specialty:
            queryset = queryset.filter(specialty__icontains=specialty)
        return queryset


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.prefetch_related("schedules").all()
    serializer_class = DoctorSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsAdminUser()]
        return [AllowAny()]


class DoctorScheduleListCreateView(generics.ListCreateAPIView):
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsStaffOrDoctor]

    def get_queryset(self):
        queryset = DoctorSchedule.objects.select_related("doctor").all()
        user = self.request.user
        doctor = get_doctor(user)

        if user.is_staff:
            doctor_id = self.request.query_params.get("doctor")
            if doctor_id:
                queryset = queryset.filter(doctor_id=doctor_id)
            return queryset

        return queryset.filter(doctor=doctor)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save()
            return
        serializer.save(doctor=get_doctor(self.request.user))


class CabinetListCreateView(generics.ListCreateAPIView):
    queryset = Cabinet.objects.select_related("responsible").all()
    serializer_class = CabinetSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsStaffOrDoctor()]


class CabinetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cabinet.objects.select_related("responsible").all()
    serializer_class = CabinetSerializer
    permission_classes = [IsAdminUser]


class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "specialty"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminUser]


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["last_name", "first_name", "phone", "card_number"]
    ordering = ["last_name"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [IsStaffDoctorOrPatient()]

    def get_queryset(self):
        user = self.request.user
        queryset = Patient.objects.all()

        if user.is_staff:
            return queryset

        # Doctor may list all cards to open a visit; UI "my patients"
        # also uses /analytics/doctor-patients/ for visit history.
        doctor = get_doctor(user)
        if doctor:
            return queryset

        patient = get_patient(user)
        if patient:
            return queryset.filter(pk=patient.pk)

        return queryset.none()

    def create(self, request, *args, **kwargs):
        user = request.user

        if not user.is_staff and get_patient(user):
            return Response(
                {"detail": "Medical card already exists for this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_staff and get_doctor(user):
            return Response(
                {"detail": "Doctors cannot create patient cards for themselves."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff:
            serializer.save()
            return
        serializer.save(user=user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return [IsStaffDoctorOrPatient()]

    def get_queryset(self):
        user = self.request.user
        queryset = Patient.objects.all()

        if user.is_staff:
            return queryset

        doctor = get_doctor(user)
        if doctor:
            return queryset

        patient = get_patient(user)
        if patient:
            return queryset.filter(pk=patient.pk)

        return queryset.none()


class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["visited_at", "cost"]
    ordering = ["-visited_at"]

    def get_permissions(self):
        return [IsStaffDoctorOrPatient()]

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related(
            "patient",
            "doctor",
            "cabinet",
            "service",
        ).all()

        if user.is_staff:
            doctor_id = self.request.query_params.get("doctor")
            patient_id = self.request.query_params.get("patient")
            is_paid = self.request.query_params.get("is_paid")
            if doctor_id:
                queryset = queryset.filter(doctor_id=doctor_id)
            if patient_id:
                queryset = queryset.filter(patient_id=patient_id)
            if is_paid is not None:
                queryset = queryset.filter(is_paid=is_paid.lower() == "true")
            return queryset

        doctor = get_doctor(user)
        if doctor:
            return queryset.filter(doctor=doctor)

        patient = get_patient(user)
        if patient:
            return queryset.filter(patient=patient)

        return queryset.none()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        doctor = get_doctor(request.user)
        patient = get_patient(request.user)

        if request.user.is_staff:
            if not data.get("doctor"):
                raise ValidationError({"doctor": "This field is required."})
            if not data.get("patient"):
                raise ValidationError({"patient": "This field is required."})
        elif doctor:
            data["doctor"] = doctor.id
            if not data.get("patient"):
                raise ValidationError({"patient": "This field is required."})
        elif patient:
            # Patient books a slot: self only, diagnosis filled later by doctor.
            data["patient"] = patient.id
            if not data.get("doctor"):
                raise ValidationError({"doctor": "This field is required."})
            data.setdefault("diagnosis", "")
            data.setdefault("condition", "")
            data.setdefault("recommendations", "")
        else:
            raise ValidationError(
                {"detail": "Complete a medical card before booking."},
            )

        if not data.get("service"):
            raise ValidationError({"service": "This field is required."})
        if not data.get("visited_at"):
            raise ValidationError({"visited_at": "This field is required."})

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        if self.request.method in ("PUT", "PATCH"):
            return [IsStaffOrDoctor()]
        return [IsStaffDoctorOrPatient()]

    def get_queryset(self):
        return AppointmentListCreateView.get_queryset(self)


class AppointmentPayView(APIView):
    """
    AppointmentPayView

    Patient pays own visit; staff can mark any visit paid.
    """

    permission_classes = [IsStaffDoctorOrPatient]

    def patch(self, request, pk):
        appointment = get_object_or_404(
            AppointmentListCreateView.get_queryset(self),
            pk=pk,
        )

        patient = get_patient(request.user)
        if (
            not request.user.is_staff
            and patient
            and appointment.patient_id != patient.id
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if get_doctor(request.user) and not request.user.is_staff:
            return Response(
                {"detail": "Doctors cannot mark payments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        appointment.is_paid = True
        appointment.save(update_fields=["is_paid"])
        return Response(AppointmentSerializer(appointment).data)


class AnalyticsDoctorPatientsView(APIView):
    permission_classes = [IsStaffOrDoctor]

    def get(self, request):
        doctor = get_doctor(request.user)
        doctor_id = request.query_params.get("doctor")

        if request.user.is_staff:
            if not doctor_id:
                return Response(
                    {"detail": "Query param `doctor` is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            doctor_id = doctor.id

        appointments = (
            Appointment.objects.filter(doctor_id=doctor_id)
            .select_related("patient")
            .order_by("patient__last_name", "patient__first_name", "visited_at")
        )
        result = [
            {
                "patient": item.patient.full_name,
                "visited_at": item.visited_at,
                "cost": item.cost,
                "is_paid": item.is_paid,
                "diagnosis": item.diagnosis,
            }
            for item in appointments
        ]
        return Response(result)


class AnalyticsOtolaryngologyPatientsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        patients = (
            Patient.objects.filter(
                birth_date__year__gt=1987,
                appointments__doctor__specialty__icontains="толаринголог",
            )
            .distinct()
            .order_by("last_name")
        )
        return Response(
            [
                {
                    "full_name": patient.full_name,
                    "phone": patient.phone,
                    "birth_date": patient.birth_date,
                }
                for patient in patients
            ]
        )


class AnalyticsDoctorsByWeekdayView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        weekday = request.query_params.get("weekday")
        if weekday is None:
            return Response(
                {"detail": "Query param `weekday` (0-6) is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        doctors = Doctor.objects.filter(
            schedules__weekday=int(weekday),
            schedules__is_working=True,
        ).distinct()
        return Response(DoctorSerializer(doctors, many=True).data)


class AnalyticsAppointmentsByDateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        rows = (
            Appointment.objects.annotate(day=TruncDate("visited_at"))
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )
        return Response(list(rows))


class AnalyticsCostByDayAndDoctorView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        by_day = (
            Appointment.objects.annotate(day=TruncDate("visited_at"))
            .values("day")
            .annotate(total_cost=Sum("cost"))
            .order_by("day")
        )
        by_doctor = (
            Appointment.objects.values(
                "doctor_id",
                "doctor__last_name",
                "doctor__first_name",
            )
            .annotate(total_cost=Sum("cost"))
            .order_by("-total_cost")
        )
        return Response(
            {
                "by_day": list(by_day),
                "by_doctor": list(by_doctor),
            }
        )


class AnalyticsPaidPatientsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        patients = (
            Patient.objects.filter(appointments__is_paid=True)
            .distinct()
            .order_by("last_name")
        )
        return Response(PatientSerializer(patients, many=True).data)


class AnalyticsDoctorsReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from = request.query_params.get("from")
        date_to = request.query_params.get("to")

        appointments = Appointment.objects.select_related("patient", "doctor")
        if date_from:
            appointments = appointments.filter(visited_at__date__gte=date_from)
        if date_to:
            appointments = appointments.filter(visited_at__date__lte=date_to)

        report = {}
        for item in appointments.order_by("doctor__last_name", "visited_at"):
            key = item.doctor_id
            if key not in report:
                report[key] = {
                    "doctor": item.doctor.full_name,
                    "specialty": item.doctor.specialty,
                    "patients": [],
                    "total_income": Decimal("0.00"),
                }
            report[key]["patients"].append(
                {
                    "patient": item.patient.full_name,
                    "visited_at": item.visited_at,
                    "diagnosis": item.diagnosis,
                    "cost": item.cost,
                    "is_paid": item.is_paid,
                }
            )
            report[key]["total_income"] += item.cost

        return Response(list(report.values()))
