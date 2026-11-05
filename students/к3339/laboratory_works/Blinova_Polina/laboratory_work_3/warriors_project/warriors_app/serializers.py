from rest_framework import serializers
from .models import CarOwner, Car, Ownership, DriverLicense


class CarOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarOwner
        fields = '__all__'


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'


class OwnershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ownership
        fields = '__all__'


class DriverLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLicense
        fields = '__all__'


class OwnershipNestedSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)

    class Meta:
        model = Ownership
        fields = '__all__'


class DriverLicenseNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLicense
        fields = ('id', 'license_number', 'license_type', 'issue_date')


class CarOwnerNestedSerializer(serializers.ModelSerializer):
    licenses = DriverLicenseNestedSerializer(many=True, read_only=True)
    ownerships = OwnershipNestedSerializer(many=True, read_only=True)

    class Meta:
        model = CarOwner
        fields = '__all__'


class CarOwnerWithCarsSerializer(serializers.ModelSerializer):
    ownerships = OwnershipNestedSerializer(many=True, read_only=True)

    class Meta:
        model = CarOwner
        fields = ('id', 'last_name', 'first_name', 'birth_date', 'ownerships')


class CarWithOwnersSerializer(serializers.ModelSerializer):
    ownerships = OwnershipNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = '__all__'