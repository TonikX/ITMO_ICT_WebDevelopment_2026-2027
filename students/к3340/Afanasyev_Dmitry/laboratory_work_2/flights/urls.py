from django.urls import path
from . import views

urlpatterns = [
    path('', views.flight_list, name='flight_list'),
    path('flights/new/', views.flight_edit, name='flight_create'),
    path('flights/<int:pk>/', views.flight_detail, name='flight_detail'),
    path('flights/<int:pk>/edit/', views.flight_edit, name='flight_edit'),
    path('flights/<int:pk>/book/', views.booking_create, name='booking_create'),
    path('flights/<int:pk>/review/', views.review_create, name='review_create'),
    path('flights/<int:pk>/passengers/', views.passenger_list, name='passengers'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:pk>/edit/', views.booking_edit, name='booking_edit'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    path('bookings/<int:pk>/check-in/', views.check_in, name='check_in'),
]
