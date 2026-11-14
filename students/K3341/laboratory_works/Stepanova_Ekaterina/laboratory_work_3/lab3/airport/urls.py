from django.urls import path
from .views import *

urlpatterns = [
    # компания
    path('companies/', CompanyListView.as_view()),
    path('companies/create/', CompanyCreateView.as_view()),
    path('companies/update/<int:pk>/', CompanyUpdateView.as_view()),
    path('companies/delete/<int:pk>/', CompanyDeleteView.as_view()),

    # тип компании
    path('companies/type/create/', CompanyTypeCreateView.as_view()),
    path('companies/type/update_delete/<int:pk>/', CompanyTypeUpdateDeleteView.as_view()),

    # работник
    path('employees/', EmployeeListView.as_view()),
    path('employees/<int:pk>/', EmployeeDetailView.as_view()),
    path('employees/create/', EmployeeCreateView.as_view()),
    path('employees/update_delete/<int:pk>/', EmployeeUpdateDeleteView.as_view()),

    # тип воздушного судна
    path('aircraft/type/create/', AircraftTypeCreateView.as_view()),
    path('aircraft/type/update_delete/<int:pk>/', AircraftTypeUpdateDeleteView.as_view()),

    # самолет
    path('aircrafts/', AircraftListView.as_view()),
    path('aircrafts/create/', AircraftCreateView.as_view()),
    path('aircrafts/update/<int:pk>/', AircraftUpdateView.as_view()),
    path('aircrafts/delete/<int:pk>/', AircraftDeleteView.as_view()),

    # все что связано с географией
    path('countries/', CountryListCreateView.as_view()),
    path('countries/<int:pk>/', CountryUpdateDeleteView.as_view()),
    path('cities/', CityListCreateView.as_view()),
    path('cities/<int:pk>/', CityUpdateDeleteView.as_view()),
    path('airports/', AirportListCreateView.as_view()),
    path('airports/<int:pk>/', AirportUpdateDeleteView.as_view()),
    path('routes/', RouteListCreateView.as_view()),
    path('routes/<int:pk>/', RouteUpdateDeleteView.as_view()),

    # должности
    path('positions/', PositionListCreateView.as_view()),
    path('positions/<int:pk>/', PositionUpdateDeleteView.as_view()),

    # экипажи
    path('crews/', CrewListView.as_view()),
    path('crews/<int:pk>/', CrewDetailView.as_view()),
    path('crews/create/', CrewCreateView.as_view()),
    path('crews/edit/<int:pk>/', CrewUpdateDeleteView.as_view()),
    path('crew-members/', CrewMemberListCreateView.as_view()),
    path('crew-members/<int:pk>/', CrewMemberUpdateDeleteView.as_view()),

    # рейсы
    path('flights/', FlightListView.as_view()),
    path('flights/<int:pk>/', FlightDetailView.as_view()),
    path('flights/create/', FlightCreateView.as_view()),
    path('flights/edit/<int:pk>/', FlightUpdateDeleteView.as_view()),

    # остановки
    path('transit-stops/', TransitStopListCreateView.as_view()),
    path('transit-stops/<int:pk>/', TransitStopUpdateDeleteView.as_view()),



]
