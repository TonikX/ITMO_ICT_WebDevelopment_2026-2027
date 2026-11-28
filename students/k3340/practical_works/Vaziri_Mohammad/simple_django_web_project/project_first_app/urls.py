from django.urls import path

from . import views

urlpatterns = [
    path("", views.owner_list, name="home"),
    # Практика 2.1: http://127.0.0.1:8000/owner/1
    path("owner/<int:owner_id>/", views.owner_detail, name="owner_detail"),
    # Практика 2.2: владельцы (FBV)
    path("owners/", views.owner_list, name="owner_list"),
    path("owners/create/", views.owner_create, name="owner_create"),
    # Практика 2.2: автомобили (CBV)
    path("cars/", views.CarListView.as_view(), name="car_list"),
    path("cars/create/", views.CarCreateView.as_view(), name="car_create"),
    path("cars/<int:pk>/", views.CarDetailView.as_view(), name="car_detail"),
    path("cars/<int:pk>/update/", views.CarUpdateView.as_view(), name="car_update"),
    path("cars/<int:pk>/delete/", views.CarDeleteView.as_view(), name="car_delete"),
]
