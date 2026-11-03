from django.urls import path
from .views import (
    CarOwnerListAPIView, CarListCreateAPIView,
    CarOwnerListGenericView, CarOwnerDetailGenericView,
    CarOwnerWithCarsView,
    CarListGenericView, CarDetailGenericView,
    OwnershipListGenericView, OwnershipDetailGenericView,
    DriverLicenseListGenericView, DriverLicenseDetailGenericView,
)

app_name = 'warriors_app'

urlpatterns = [
    path('owners/api/', CarOwnerListAPIView.as_view()),
    path('cars/api/', CarListCreateAPIView.as_view()),

    path('owners/', CarOwnerListGenericView.as_view()),
    path('owners/<int:pk>/', CarOwnerDetailGenericView.as_view()),
    path('owners/<int:pk>/cars/', CarOwnerWithCarsView.as_view()),

    path('cars/', CarListGenericView.as_view()),
    path('cars/<int:pk>/', CarDetailGenericView.as_view()),

    path('ownerships/', OwnershipListGenericView.as_view()),
    path('ownerships/<int:pk>/', OwnershipDetailGenericView.as_view()),

    path('licenses/', DriverLicenseListGenericView.as_view()),
    path('licenses/<int:pk>/', DriverLicenseDetailGenericView.as_view()),
]