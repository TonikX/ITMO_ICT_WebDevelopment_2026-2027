from rest_framework import serializers
from .models import (
    CompanyType, Company, AircraftType, Aircraft, Airport, Route,
    Crew, Employee, Flight, TransitStop, CrewMember, Admission,
)

class CompanyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyType
        fields = ["id", "name"]


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "company_type"]


class AircraftTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AircraftType
        fields = ["id", "model", "manufacturer"]


class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = ["id", "register_number", "aircraft_type", "company",
                  "seats", "speed", "status"]


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "city"]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["id", "departure_airport", "destination_airport", "distance"]


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "name"]


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "full_name", "birth_date", "education",
                  "experience_years", "passport_data", "company",
                  "employment_status", "hire_date", "fire_date"]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ["id", "flight_number", "route", "aircraft", "crew",
                  "departure_dt", "arrival_dt", "tickets_sold"]


class TransitStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransitStop
        fields = ["id", "flight", "airport", "arrival_dt", "departure_dt"]


class CrewMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewMember
        fields = ["id", "crew", "employee", "role"]


class AdmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admission
        fields = ["id", "employee", "flight", "is_allowed", "issue_date"]


class CrewMemberNestedSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = CrewMember
        fields = ["employee", "role"]


class CrewFullSerializer(serializers.ModelSerializer):
    members = CrewMemberNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = ["id", "name", "members"]


class TransitStopNestedSerializer(serializers.ModelSerializer):
    airport = AirportSerializer(read_only=True)

    class Meta:
        model = TransitStop
        fields = ["airport", "arrival_dt", "departure_dt"]


class FlightFullSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    aircraft = AircraftSerializer(read_only=True)
    crew = CrewFullSerializer(read_only=True)
    transit_stops = TransitStopNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = ["id", "flight_number", "route", "aircraft", "crew",
                  "departure_dt", "arrival_dt", "tickets_sold",
                  "transit_stops"]


class AircraftFullSerializer(serializers.ModelSerializer):
    flights = FlightSerializer(many=True, read_only=True)
    aircraft_type = AircraftTypeSerializer(read_only=True)

    class Meta:
        model = Aircraft
        fields = ["id", "register_number", "aircraft_type", "company",
                  "seats", "speed", "status", "flights"]


class CompanyFullSerializer(serializers.ModelSerializer):
    aircrafts = AircraftSerializer(many=True, read_only=True)
    employees = EmployeeSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ["id", "name", "company_type", "aircrafts", "employees"]

class EmployeeFullSerializer(serializers.ModelSerializer):
    crews = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = ["id", "full_name", "birth_date", "education",
                  "experience_years", "passport_data", "company",
                  "employment_status", "hire_date", "fire_date", "crews"]