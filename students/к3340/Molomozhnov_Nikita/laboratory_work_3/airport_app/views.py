from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import (
    CompanyType, Company, AircraftType, Aircraft, Airport, Route,
    Crew, Employee, Flight, TransitStop, CrewMember, Admission,
)
from .serializers import (
    CompanyTypeSerializer, CompanySerializer, CompanyFullSerializer,
    AircraftTypeSerializer, AircraftSerializer, AircraftFullSerializer,
    AirportSerializer, RouteSerializer, CrewSerializer, CrewFullSerializer,
    EmployeeSerializer, EmployeeFullSerializer, FlightSerializer,
    FlightFullSerializer, TransitStopSerializer, CrewMemberSerializer,
    AdmissionSerializer,
)


class CompanyListCreateView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyFullSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AircraftListCreateView(generics.ListCreateAPIView):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftSerializer


class AircraftDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Aircraft.objects.all()
    serializer_class = AircraftFullSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FlightListCreateView(generics.ListCreateAPIView):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


class FlightDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Flight.objects.all()
    serializer_class = FlightFullSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CrewListCreateView(generics.ListCreateAPIView):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class CrewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Crew.objects.all()
    serializer_class = CrewFullSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeFullSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AirportListCreateView(generics.ListCreateAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class CrewMemberListCreateView(generics.ListCreateAPIView):
    queryset = CrewMember.objects.all()
    serializer_class = CrewMemberSerializer


class AdmissionListCreateView(generics.ListCreateAPIView):
    queryset = Admission.objects.all()
    serializer_class = AdmissionSerializer


class TransitStopListCreateView(generics.ListCreateAPIView):
    queryset = TransitStop.objects.all()
    serializer_class = TransitStopSerializer

class CompanyTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanyType.objects.all()
    serializer_class = CompanyTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AircraftTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AircraftType.objects.all()
    serializer_class = AircraftTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AirportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class RouteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TransitStopDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TransitStop.objects.all()
    serializer_class = TransitStopSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CrewMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CrewMember.objects.all()
    serializer_class = CrewMemberSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AdmissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Admission.objects.all()
    serializer_class = AdmissionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
