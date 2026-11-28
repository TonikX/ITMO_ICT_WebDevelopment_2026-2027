from rest_framework import serializers
from .models import CarOwner, Car, Ownership, DriverLicense
from django.contrib.auth import get_user_model

User = get_user_model()

class DriverLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLicense
        fields = ["license_number", "license_type", "issue_date"]


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ["id", "state_number", "brand", "model_name", "color"]


class OwnershipSerializer(serializers.ModelSerializer):
    car = CarSerializer(read_only=True)

    class Meta:
        model = Ownership
        fields = ["car", "start_date", "end_date"]


class CarOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarOwner
        fields = ["id", "first_name", "last_name", "birth_date"]


class CarOwnerFullSerializer(serializers.ModelSerializer):
    license = DriverLicenseSerializer(read_only=True)
    ownerships = OwnershipSerializer(many=True, read_only=True)

    class Meta:
        model = CarOwner
        fields = ["id", "first_name", "last_name", "birth_date",
                  "license", "ownerships"]


class CarFullSerializer(serializers.ModelSerializer):
    owners = CarOwnerSerializer(many=True, read_only=True)
    ownerships = OwnershipSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = ["id", "state_number", "brand", "model_name", "color",
                  "owners", "ownerships"]
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email",
                  "passport_number", "home_address", "nationality"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password",
                  "passport_number", "home_address", "nationality"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user