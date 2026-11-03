from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import CarOwner, Car, Ownership, DriverLicense
from .serializers import (
    CarOwnerSerializer, CarSerializer, OwnershipSerializer,
    DriverLicenseSerializer, CarOwnerNestedSerializer,
    CarOwnerWithCarsSerializer, CarWithOwnersSerializer,
)


class CarOwnerListAPIView(APIView):
    def get(self, request):
        owners = CarOwner.objects.all()
        serializer = CarOwnerSerializer(owners, many=True)
        return Response({'owners': serializer.data})

    def post(self, request):
        serializer = CarOwnerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'success': 'Владелец создан'})


class CarListCreateAPIView(APIView):
    def get(self, request):
        cars = Car.objects.all()
        return Response({'cars': CarSerializer(cars, many=True).data})

    def post(self, request):
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'success': 'Автомобиль создан'})


class CarOwnerListGenericView(generics.ListCreateAPIView):
    queryset = CarOwner.objects.all()
    serializer_class = CarOwnerSerializer


class CarOwnerDetailGenericView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CarOwner.objects.all()
    serializer_class = CarOwnerNestedSerializer


class CarOwnerWithCarsView(generics.RetrieveAPIView):
    queryset = CarOwner.objects.all()
    serializer_class = CarOwnerWithCarsSerializer


class CarListGenericView(generics.ListCreateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer


class CarDetailGenericView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Car.objects.all()
    serializer_class = CarWithOwnersSerializer


class OwnershipListGenericView(generics.ListCreateAPIView):
    queryset = Ownership.objects.all()
    serializer_class = OwnershipSerializer


class OwnershipDetailGenericView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ownership.objects.all()
    serializer_class = OwnershipSerializer


class DriverLicenseListGenericView(generics.ListCreateAPIView):
    queryset = DriverLicense.objects.all()
    serializer_class = DriverLicenseSerializer


class DriverLicenseDetailGenericView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DriverLicense.objects.all()
    serializer_class = DriverLicenseSerializer