from django.urls import path

from . import views

urlpatterns = [
    path('owners/', views.owners_list, name='owners_list'),
    path('owners/create/', views.owner_create, name='owner_create'),
    path('owner/<int:owner_id>/', views.owner_detail, name='owner_detail'),

    path('cars/', views.CarListView.as_view(), name='cars_list'),
    path('cars/create/', views.CarCreateView.as_view(), name='car_create'),
    path('cars/<int:pk>/', views.CarDetailView.as_view(), name='car_detail'),
    path('cars/<int:pk>/edit/', views.CarUpdateView.as_view(), name='car_edit'),
    path('cars/<int:pk>/delete/', views.CarDeleteView.as_view(), name='car_delete'),
]
