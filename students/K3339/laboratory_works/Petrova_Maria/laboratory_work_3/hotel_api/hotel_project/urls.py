from django.contrib import admin
from django.urls import include, path

from hotel_app import page_views

urlpatterns = [
    path("", page_views.rooms, name="hotel-rooms"),
    path("guests/", page_views.guests, name="hotel-guests"),
    path("check-in/", page_views.check_in, name="hotel-check-in"),
    path("admin/", admin.site.urls),
    path("api/", include("hotel_app.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
