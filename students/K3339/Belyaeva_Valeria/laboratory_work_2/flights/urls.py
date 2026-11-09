from django.urls import path
from . import views

urlpatterns = [
    path('', views.flight_list, name='flight_list'),
    path('flights/<int:pk>/', views.flight_detail, name='flight_detail'),
    path('flights/<int:flight_pk>/book/', views.booking_edit, name='booking_create'),
    path('bookings/', views.bookings, name='bookings'),
    path('bookings/<int:pk>/edit/', views.booking_edit, name='booking_edit'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    path('flights/<int:pk>/passengers/', views.passengers, name='passengers'),
    path('flights/<int:flight_pk>/passengers/add/', views.staff_booking, name='staff_booking_create'),
    path('flights/<int:flight_pk>/passengers/<int:pk>/', views.staff_booking, name='staff_booking_edit'),
    path('login/', views.SignInView.as_view(), name='login'),
    path('logout/', views.SignOutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
]
