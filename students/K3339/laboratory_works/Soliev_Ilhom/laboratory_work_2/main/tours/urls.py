from django.urls import path

from . import views

urlpatterns = [
    path("", views.tour_list, name="tour_list"),
    path("register/", views.register, name="register"),
    path("tours/<int:pk>/", views.tour_detail, name="tour_detail"),
    path("tours/<int:pk>/book/", views.booking_create, name="booking_create"),
    path("tours/<int:pk>/reviews/", views.review_create, name="review_create"),
    path("bookings/", views.my_bookings, name="my_bookings"),
    path("bookings/<int:pk>/edit/", views.booking_edit, name="booking_edit"),
    path("bookings/<int:pk>/delete/", views.booking_delete, name="booking_delete"),
    path("sales/", views.sales, name="sales"),
    path("manage/bookings/", views.booking_manage, name="booking_manage"),
    path("manage/bookings/<int:pk>/confirm/", views.booking_confirm, name="booking_confirm"),
]
