from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    
    path("tours/<int:pk>/", views.tour_detail, name="tour_detail"),
    
    path("register/", views.register, name="register"),
    
    path(
        "login/",
        views.NordwayLoginView.as_view(),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="home"),
        name="logout",
    ),
    
    path(
        "tours/<int:pk>/book/",
        views.booking_form,
        name="booking_form",
    ),
    
    path(
        "my-bookings/",
        views.my_bookings,
        name="my_bookings",
    ),
    
    path(
        "bookings/<int:pk>/cancel/",
        views.cancel_booking,
        name="cancel_booking",
    ),
    
    path(
        "bookings/<int:pk>/edit/",
        views.edit_booking,
        name="edit_booking",
    ),
    
    path(
        "tours/<int:pk>/review/",
        views.create_review,
        name="create_review",
    ),
    
    path(
        "statistics/countries/",
        views.country_statistics,
        name="country_statistics",
    ),
]
