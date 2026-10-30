from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Reservation, Review, Tour
from .serializers import (
    RegisterSerializer,
    ReservationSerializer,
    ReviewSerializer,
    TourSerializer,
    UserSerializer,
)

class TourListView(generics.ListAPIView):
    serializer_class = TourSerializer
    permission_classes = [AllowAny]
    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]
    search_fields = [
        "name",
        "description",
        "country__name",
        "agency__name",
    ]
    ordering_fields = [
        "price",
        "start_date",
        "end_date",
        "name",
    ]
    ordering = ["start_date"]

    def get_queryset(self):
        queryset = Tour.objects.select_related(
            "country",
            "agency",
        ).all()

        country = self.request.query_params.get("country")
        agency = self.request.query_params.get("agency")

        if country:
            queryset = queryset.filter(
                country__name__icontains=country,
            )

        if agency:
            queryset = queryset.filter(
                agency__name__icontains=agency,
            )

        return queryset

class TourDetailView(generics.RetrieveAPIView):
    queryset = Tour.objects.select_related(
        "country",
        "agency",
    ).all()
    serializer_class = TourSerializer
    permission_classes = [AllowAny]

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class ReservationListCreateView(generics.ListCreateAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(
            user=self.request.user,
        ).select_related(
            "user",
            "tour",
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
        )

class ReservationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(
            user=self.request.user,
        ).select_related(
            "user",
            "tour",
        )

    def perform_update(self, serializer):
                                                                
        serializer.save(is_confirmed=False)

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = Review.objects.select_related(
            "user",
            "tour",
        ).all()

        tour_id = self.request.query_params.get("tour")

        if tour_id:
            queryset = queryset.filter(tour_id=tour_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
        )

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(
            user=self.request.user,
        ).select_related(
            "user",
            "tour",
        )

class AdminReservationListView(generics.ListAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Reservation.objects.select_related(
            "user",
            "tour",
        ).all()

class AdminReservationConfirmView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        reservation.is_confirmed = True
        reservation.save(update_fields=["is_confirmed"])
        return Response(ReservationSerializer(reservation).data)

class SoldToursByCountryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        reservations = (
            Reservation.objects.filter(is_confirmed=True)
            .select_related(
                "tour",
                "tour__country",
                "user",
            )
            .order_by(
                "tour__country__name",
                "tour__name",
            )
        )

        result = [
            {
                "country": item.tour.country.name,
                "tour": item.tour.name,
                "user": item.user.username,
                "start_date": item.start_date,
                "end_date": item.end_date,
            }
            for item in reservations
        ]

        return Response(result)
