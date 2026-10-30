from django.urls import path

from .views import (
    AnalyticsAppointmentsByDateView,
    AnalyticsCostByDayAndDoctorView,
    AnalyticsDoctorPatientsView,
    AnalyticsDoctorsByWeekdayView,
    AnalyticsDoctorsReportView,
    AnalyticsOtolaryngologyPatientsView,
    AnalyticsPaidPatientsView,
    AppointmentDetailView,
    AppointmentListCreateView,
    AppointmentPayView,
    CabinetDetailView,
    CabinetListCreateView,
    CurrentUserView,
    DoctorDetailView,
    DoctorListCreateView,
    DoctorScheduleListCreateView,
    PatientDetailView,
    PatientListCreateView,
    ServiceDetailView,
    ServiceListCreateView,
)

urlpatterns = [
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("doctors/", DoctorListCreateView.as_view(), name="doctor-list"),
    path(
        "doctors/<int:pk>/",
        DoctorDetailView.as_view(),
        name="doctor-detail",
    ),
    path(
        "schedules/",
        DoctorScheduleListCreateView.as_view(),
        name="schedule-list",
    ),
    path("cabinets/", CabinetListCreateView.as_view(), name="cabinet-list"),
    path(
        "cabinets/<int:pk>/",
        CabinetDetailView.as_view(),
        name="cabinet-detail",
    ),
    path("services/", ServiceListCreateView.as_view(), name="service-list"),
    path(
        "services/<int:pk>/",
        ServiceDetailView.as_view(),
        name="service-detail",
    ),
    path("patients/", PatientListCreateView.as_view(), name="patient-list"),
    path(
        "patients/<int:pk>/",
        PatientDetailView.as_view(),
        name="patient-detail",
    ),
    path(
        "appointments/",
        AppointmentListCreateView.as_view(),
        name="appointment-list",
    ),
    path(
        "appointments/<int:pk>/",
        AppointmentDetailView.as_view(),
        name="appointment-detail",
    ),
    path(
        "appointments/<int:pk>/pay/",
        AppointmentPayView.as_view(),
        name="appointment-pay",
    ),
    path(
        "analytics/doctor-patients/",
        AnalyticsDoctorPatientsView.as_view(),
        name="analytics-doctor-patients",
    ),
    path(
        "analytics/ent-patients/",
        AnalyticsOtolaryngologyPatientsView.as_view(),
        name="analytics-ent-patients",
    ),
    path(
        "analytics/doctors-by-weekday/",
        AnalyticsDoctorsByWeekdayView.as_view(),
        name="analytics-doctors-weekday",
    ),
    path(
        "analytics/appointments-by-date/",
        AnalyticsAppointmentsByDateView.as_view(),
        name="analytics-appointments-by-date",
    ),
    path(
        "analytics/costs/",
        AnalyticsCostByDayAndDoctorView.as_view(),
        name="analytics-costs",
    ),
    path(
        "analytics/paid-patients/",
        AnalyticsPaidPatientsView.as_view(),
        name="analytics-paid-patients",
    ),
    path(
        "analytics/doctors-report/",
        AnalyticsDoctorsReportView.as_view(),
        name="analytics-doctors-report",
    ),
]
