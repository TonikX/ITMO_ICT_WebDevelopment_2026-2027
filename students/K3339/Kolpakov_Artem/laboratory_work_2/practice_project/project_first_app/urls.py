from django.urls import path

from . import views


urlpatterns = [
    path("", views.owner_list, name="practice_home"),
    path("owners/", views.owner_list, name="owner_list"),
    path("owner/<int:owner_id>/", views.owner_detail, name="owner_detail"),
    path("register/", views.register, name="register"),
    path("cars/", views.CarListView.as_view(), name="car_list"),
    path("cars/create/", views.CarCreateView.as_view(), name="car_create"),
    path("cars/<int:pk>/", views.CarDetailView.as_view(), name="car_detail"),
    path("cars/<int:pk>/edit/", views.CarUpdateView.as_view(), name="car_update"),
    path("cars/<int:pk>/delete/", views.CarDeleteView.as_view(), name="car_delete"),
]
