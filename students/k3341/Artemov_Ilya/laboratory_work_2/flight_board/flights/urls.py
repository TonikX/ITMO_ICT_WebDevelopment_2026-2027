from django.urls import path
from . import views

app_name = "flights"
urlpatterns = [
    path("", views.flight_list, name="list"),
    path("flights/<int:pk>/", views.flight_detail, name="detail"),
    path("flights/<int:pk>/passengers/", views.passenger_list, name="passengers"),
    path("flights/<int:pk>/reserve/", views.reservation_create, name="reserve"),
    path("flights/<int:pk>/reviews/new/", views.review_create, name="review_create"),
    path("flights/<int:pk>/passengers/new/", views.staff_reservation_create, name="staff_reserve"),
    path("reservations/", views.my_reservations, name="my_reservations"),
    path("reservations/<int:pk>/edit/", views.reservation_update, name="reservation_update"),
    path("reservations/<int:pk>/delete/", views.reservation_delete, name="reservation_delete"),
    path("reservations/<int:pk>/check-in/", views.check_in, name="check_in"),
]
