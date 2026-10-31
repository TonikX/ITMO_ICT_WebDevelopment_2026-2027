from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('flights/<int:flight_id>/', views.flight_detail, name='flight_detail'),
    path('flights/<int:flight_id>/reserve/', views.create_reservation, name='create_reservation'),
    path('reservations/', views.my_reservations, name='my_reservations'),
    path('reservations/<int:reservation_id>/edit/', views.edit_reservation, name='edit_reservation'),
    path('reservations/<int:reservation_id>/delete/', views.delete_reservation, name='delete_reservation'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('flights/<int:flight_id>/review/', views.create_review, name='create_review'),
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('flights/<int:flight_id>/passenger/add/', views.create_passenger, name='create_passenger'),
]
