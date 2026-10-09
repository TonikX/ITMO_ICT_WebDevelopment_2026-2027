from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Agency, Country, Reservation, Review, Tour

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")

class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ("id", "name")

class TourSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    agency = AgencySerializer(read_only=True)

    class Meta:
        model = Tour
        fields = (
            "id",
            "name",
            "agency",
            "country",
            "description",
            "start_date",
            "end_date",
            "payment_terms",
            "price",
        )

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "is_staff",
        )

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
        )

    def create(self, validated_data):
                                                                                           
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )

class ReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tour_name = serializers.CharField(
        source="tour.name",
        read_only=True,
    )

    class Meta:
        model = Reservation
        fields = (
            "id",
            "user",
            "tour",
            "tour_name",
            "start_date",
            "end_date",
            "created_at",
            "is_confirmed",
        )
        read_only_fields = (
            "id",
            "user",
            "tour_name",
            "created_at",
            "is_confirmed",
        )

    def create(self, validated_data):
        tour = validated_data["tour"]
        validated_data.setdefault("start_date", tour.start_date)
        validated_data.setdefault("end_date", tour.end_date)
        return super().create(validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tour_name = serializers.CharField(
        source="tour.name",
        read_only=True,
    )

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "tour",
            "tour_name",
            "text",
            "rating",
            "start_date",
            "end_date",
            "created_at",
        )
        read_only_fields = (
            "id",
            "user",
            "tour_name",
            "start_date",
            "end_date",
            "created_at",
        )

    def create(self, validated_data):
        tour = validated_data["tour"]
        validated_data.setdefault("start_date", tour.start_date)
        validated_data.setdefault("end_date", tour.end_date)
        return super().create(validated_data)
