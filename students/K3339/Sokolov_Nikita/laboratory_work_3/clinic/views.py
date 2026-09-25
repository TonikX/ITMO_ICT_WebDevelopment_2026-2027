from datetime import datetime

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cabinet, Doctor, MedicalCard, Patient, PriceList, Visit, WorkSchedule
from .serializers import (
    CabinetSerializer,
    DoctorSerializer,
    DoctorWithPatientsSerializer,
    MedicalCardSerializer,
    MedicalCardWithVisitsSerializer,
    PatientSerializer,
    PriceListSerializer,
    VisitSerializer,
    WorkScheduleSerializer,
)


class DoctorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class DoctorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class PatientListCreateAPIView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class PatientRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class MedicalCardListCreateAPIView(generics.ListCreateAPIView):
    queryset = MedicalCard.objects.select_related("patient").all()
    serializer_class = MedicalCardSerializer


class MedicalCardRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MedicalCard.objects.select_related("patient").all()
    serializer_class = MedicalCardSerializer


class MedicalCardWithVisitsAPIView(generics.RetrieveAPIView):
    queryset = MedicalCard.objects.select_related("patient").prefetch_related(
        "visits__doctor",
        "visits__cabinet",
        "visits__price_list",
    )
    serializer_class = MedicalCardWithVisitsSerializer


class DoctorWithPatientsAPIView(generics.RetrieveAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorWithPatientsSerializer


class VisitListCreateAPIView(generics.ListCreateAPIView):
    queryset = Visit.objects.select_related(
        "medical_card__patient",
        "doctor",
        "cabinet",
        "price_list",
    ).all()
    serializer_class = VisitSerializer


class VisitRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Visit.objects.select_related(
        "medical_card__patient",
        "doctor",
        "cabinet",
        "price_list",
    ).all()
    serializer_class = VisitSerializer


class CabinetListCreateAPIView(generics.ListCreateAPIView):
    queryset = Cabinet.objects.select_related("responsible_doctor").all()
    serializer_class = CabinetSerializer


class CabinetRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cabinet.objects.select_related("responsible_doctor").all()
    serializer_class = CabinetSerializer


class PriceListListCreateAPIView(generics.ListCreateAPIView):
    queryset = PriceList.objects.all()
    serializer_class = PriceListSerializer


class PriceListRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PriceList.objects.all()
    serializer_class = PriceListSerializer


class WorkScheduleListCreateAPIView(generics.ListCreateAPIView):
    queryset = WorkSchedule.objects.select_related("doctor").all()
    serializer_class = WorkScheduleSerializer


class WorkScheduleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WorkSchedule.objects.select_related("doctor").all()
    serializer_class = WorkScheduleSerializer


class DoctorPatientsAnalyticsAPIView(APIView):
    def get(self, request, doctor_id):
        visits = (
            Visit.objects.filter(doctor_id=doctor_id)
            .select_related("medical_card__patient")
            .order_by(
                "medical_card__patient__last_name",
                "medical_card__patient__first_name",
                "visit_at",
            )
        )
        data = [
            {
                "patient": visit.medical_card.patient.fio,
                "visit_at": visit.visit_at,
                "cost": visit.cost,
            }
            for visit in visits
        ]
        return Response(data)


class OtolaryngologyPatientsAPIView(APIView):
    def get(self, request):
        patients = (
            Patient.objects.filter(
                medical_card__visits__doctor__specialty__icontains="отоларинголог",
                birth_date__year__gt=1987,
            )
            .distinct()
            .order_by("last_name", "first_name")
        )
        data = [{"fio": p.fio, "phone": p.phone, "birth_date": p.birth_date} for p in patients]
        return Response(data)


class DoctorsByWorkDateAPIView(APIView):
    def get(self, request):
        work_date = request.query_params.get("date")
        if not work_date:
            return Response({"detail": "Укажите date=YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        doctors = Doctor.objects.filter(
            schedules__work_date=work_date,
            schedules__is_working=True,
        ).distinct()
        return Response(DoctorSerializer(doctors, many=True).data)


class VisitsCountByDateAPIView(APIView):
    def get(self, request):
        rows = (
            Visit.objects.annotate(day=TruncDate("visit_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        return Response(list(rows))


class TreatmentSumsAPIView(APIView):
    def get(self, request):
        by_day = (
            Visit.objects.annotate(day=TruncDate("visit_at"))
            .values("day")
            .annotate(total=Sum("cost"))
            .order_by("day")
        )
        by_doctor = (
            Visit.objects.values("doctor_id", "doctor__last_name", "doctor__first_name")
            .annotate(total=Sum("cost"))
            .order_by("doctor__last_name")
        )
        return Response({"by_day": list(by_day), "by_doctor": list(by_doctor)})


class PaidPatientsAPIView(APIView):
    def get(self, request):
        patients = (
            Patient.objects.filter(medical_card__visits__is_paid=True)
            .distinct()
            .order_by("last_name", "first_name")
        )
        return Response(PatientSerializer(patients, many=True).data)


class DoctorPeriodReportAPIView(APIView):
    def get(self, request):
        date_from = request.query_params.get("from")
        date_to = request.query_params.get("to")
        if not date_from or not date_to:
            return Response(
                {"detail": "Укажите from=YYYY-MM-DD и to=YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        start = datetime.fromisoformat(date_from)
        end = datetime.fromisoformat(date_to)
        visits = (
            Visit.objects.filter(visit_at__date__gte=start.date(), visit_at__date__lte=end.date())
            .select_related("doctor", "medical_card__patient")
            .order_by("doctor__last_name", "visit_at")
        )
        report = {}
        for visit in visits:
            key = visit.doctor_id
            if key not in report:
                report[key] = {
                    "doctor": visit.doctor.fio,
                    "patients": [],
                    "total_income": 0,
                }
            report[key]["patients"].append(
                {
                    "patient": visit.medical_card.patient.fio,
                    "diagnosis": visit.diagnosis,
                    "cost": visit.cost,
                    "visit_at": visit.visit_at,
                }
            )
            report[key]["total_income"] += float(visit.cost)
        return Response(list(report.values()))
