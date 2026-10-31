
from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),

    path('cars/', views.CarListView.as_view(), name='car_list'),
    path('cars/create/', views.CarCreateView.as_view(), name='car_create'),
    path(
        'cars/<int:car_id>/',
        views.CarDetailView.as_view(),
        name='car_detail'
    ),
    path(
        'cars/<int:car_id>/edit/',
        views.CarUpdateView.as_view(),
        name='car_update'
    ),
    path(
        'cars/<int:car_id>/delete/',
        views.CarDeleteView.as_view(),
        name='car_delete'
    ),
]
