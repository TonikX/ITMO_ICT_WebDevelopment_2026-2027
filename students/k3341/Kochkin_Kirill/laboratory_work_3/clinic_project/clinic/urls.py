from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .analytics import (
    doctor_patients,
    ent_patients,
    working_doctors,
    appointments_by_date,
    treatment_costs,
    paid_patients,
    doctors_report
)

from .views import (
    PatientViewSet, MedicalCardViewSet,
    SpecialtyViewSet, DoctorViewSet,
    CabinetViewSet, DoctorScheduleViewSet,
    AppointmentViewSet, ServiceViewSet,
    AppointmentServiceViewSet, PaymentViewSet
)


router = DefaultRouter()

router.register('patients', PatientViewSet)
router.register('medical-cards', MedicalCardViewSet)
router.register('specialties', SpecialtyViewSet)
router.register('doctors', DoctorViewSet)
router.register('cabinets', CabinetViewSet)
router.register('schedules', DoctorScheduleViewSet)
router.register('appointments', AppointmentViewSet)
router.register('services', ServiceViewSet)
router.register('appointment-services', AppointmentServiceViewSet)
router.register('payments', PaymentViewSet)

urlpatterns = [
    path('analytics/doctor-patients/', doctor_patients),
    path('analytics/ent-patients/', ent_patients),
    path('analytics/working-doctors/', working_doctors),
    path('analytics/appointments-by-date/', appointments_by_date),
    path('analytics/treatment-costs/', treatment_costs),
    path('analytics/paid-patients/', paid_patients),
    path('reports/doctors/', doctors_report),
    path('', include(router.urls)),
]