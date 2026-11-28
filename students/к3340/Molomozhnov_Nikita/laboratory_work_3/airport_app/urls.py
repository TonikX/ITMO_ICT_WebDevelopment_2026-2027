from django.urls import path
from . import views
from .analytics import (
    AircraftMostFrequentRouteView,
    UnderfilledRoutesView,
    FlightFreeSeatsView,
    AircraftInRepairView,
    CompanyEmployeesCountView,
    CompanyAircraftsReportView,
)
from .views import (
    CompanyTypeDetailView, AircraftTypeDetailView,
    AirportDetailView, RouteDetailView,
    TransitStopDetailView, CrewMemberDetailView,
    AdmissionDetailView,
)
app_name = "airport_app"

urlpatterns = [
    path("companies/", views.CompanyListCreateView.as_view()),
    path("companies/<int:pk>/", views.CompanyDetailView.as_view()),
    path("aircrafts/", views.AircraftListCreateView.as_view()),
    path("aircrafts/<int:pk>/", views.AircraftDetailView.as_view()),
    path("flights/", views.FlightListCreateView.as_view()),
    path("flights/<int:pk>/", views.FlightDetailView.as_view()),
    path("crews/", views.CrewListCreateView.as_view()),
    path("crews/<int:pk>/", views.CrewDetailView.as_view()),
    path("employees/", views.EmployeeListCreateView.as_view()),
    path("employees/<int:pk>/", views.EmployeeDetailView.as_view()),
    path("airports/", views.AirportListCreateView.as_view()),
    path("routes/", views.RouteListCreateView.as_view()),
    path("crew-members/", views.CrewMemberListCreateView.as_view()),
    path("admissions/", views.AdmissionListCreateView.as_view()),
    path("transit-stops/", views.TransitStopListCreateView.as_view()),
    path("analytics/aircraft-most-frequent-route/", AircraftMostFrequentRouteView.as_view()),
    path("analytics/underfilled-routes/", UnderfilledRoutesView.as_view()),
    path("analytics/flights/<int:pk>/free-seats/", FlightFreeSeatsView.as_view()),
    path("analytics/aircraft-in-repair/", AircraftInRepairView.as_view()),
    path("analytics/company-employees/", CompanyEmployeesCountView.as_view()),
    path("analytics/company-aircrafts-report/", CompanyAircraftsReportView.as_view()),
    path("company-types/<int:pk>/", CompanyTypeDetailView.as_view()),
    path("aircraft-types/<int:pk>/", AircraftTypeDetailView.as_view()),
    path("airports/<int:pk>/", AirportDetailView.as_view()),
    path("routes/<int:pk>/", RouteDetailView.as_view()),
    path("transit-stops/<int:pk>/", TransitStopDetailView.as_view()),
    path("crew-members/<int:pk>/", CrewMemberDetailView.as_view()),
    path("admissions/<int:pk>/", AdmissionDetailView.as_view()),
]