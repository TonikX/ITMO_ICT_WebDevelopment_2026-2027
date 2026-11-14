from rest_framework import serializers
from .models import *


class CompanyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyType
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class AircraftTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AircraftType
        fields = '__all__'


class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        # Выводим всю информацию о пользователе, кроме зашифрованного пароля
        exclude = ['password']


# Промежуточная таблица состава экипажа
class CrewMemberSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    position_name = serializers.CharField(source='position.position_name', read_only=True)

    class Meta:
        model = CrewMember
        fields = ['id', 'crew', 'employee', 'employee_name', 'position', 'position_name']


# Экипаж с вложенным списком участников
class CrewDetailSerializer(serializers.ModelSerializer):
    members = EmployeeSerializer(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = ['crew_id', 'crew_name', 'members']


# Экипаж для создания/редактирования
class CrewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ['crew_id', 'crew_name']

class TransitStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransitStop
        fields = '__all__'


# Расширенный сериализатор рейса (показывает пересадки и читаемые связи)
class FlightDetailSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField()
    aircraft = serializers.StringRelatedField()
    crew = serializers.StringRelatedField()
    # Подтягиваем все промежуточные остановки по related_name="transit_stops"
    transit_stops = TransitStopSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = '__all__'


# Сериализатор рейса для создания и изменения через ID
class FlightCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'
