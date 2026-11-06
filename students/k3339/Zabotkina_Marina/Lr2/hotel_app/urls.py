from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.RoomListView.as_view(), name="room_list"),
    path("room/<int:pk>/", views.room_detail_view, name="room_detail"),
    path("register/", views.register_view, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("logout/", views.logout_view, name="logout"),
    path("my-bookings/", views.MyBookingsView.as_view(), name="my_bookings"),
    path(
        "booking/<int:pk>/edit/",
        views.BookingUpdateView.as_view(),
        name="booking_edit",
    ),
    path(
        "booking/<int:pk>/delete/",
        views.BookingDeleteView.as_view(),
        name="booking_delete",
    ),
    path("guests/", views.GuestListView.as_view(), name="guest_list"),
    path(
        "booking/<int:pk>/status/<str:status>/",
        views.change_booking_status,
        name="change_status",
    ),
]