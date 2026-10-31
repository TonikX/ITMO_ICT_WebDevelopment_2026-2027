from django.urls import path

from . import views

urlpatterns = [
    path("", views.room_list, name="room_list"),
    path("rooms/<int:pk>/", views.room_detail, name="room_detail"),
    path("accounts/signup/", views.signup, name="signup"),
    path("rooms/<int:room_pk>/book/", views.booking_create, name="booking_create"),
    path("rooms/<int:room_pk>/review/", views.review_create, name="review_create"),
    path("bookings/", views.my_bookings, name="my_bookings"),
    path("bookings/<int:pk>/edit/", views.booking_edit, name="booking_edit"),
    path("bookings/<int:pk>/delete/", views.booking_delete, name="booking_delete"),
    path("staff/guests/", views.guest_report, name="guest_report"),
]
