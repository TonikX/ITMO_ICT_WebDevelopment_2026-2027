"""Адреса учебных интерфейсов."""

from django.urls import path

from . import views

app_name = "practice"
urlpatterns = [
    path("owners/", views.owner_list, name="owner_list"),
    path("owner/create/", views.owner_create, name="owner_create"),
    path("owner/<int:pk>", views.owner_detail, name="owner_detail"),
    path("cars/", views.CarList.as_view(), name="car_list"),
    path("cars/create/", views.CarCreate.as_view(), name="car_create"),
    path("cars/<int:pk>/", views.CarDetail.as_view(), name="car_detail"),
    path("cars/<int:pk>/edit/", views.CarUpdate.as_view(), name="car_edit"),
    path("cars/<int:pk>/delete/", views.CarDelete.as_view(), name="car_delete"),
]
