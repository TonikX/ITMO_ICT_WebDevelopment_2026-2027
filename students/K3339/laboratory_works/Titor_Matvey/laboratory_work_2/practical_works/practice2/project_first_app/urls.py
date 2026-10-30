
from django.urls import path

from . import views

urlpatterns = [
    path('owners/', views.get_all_owners, name='owners_list'),
    path('owner/<int:pk>/', views.owner, name='owner'),
    path('owner/create/', views.create_owner, name='create_owner'),

    path('cars/', views.CarListView.as_view(), name='car_list'),
    path('cars/<int:pk>/', views.CarDetailView.as_view(), name='car_detail'),
    path('cars/create/', views.CarCreateView.as_view(), name='car_create'),
    path('cars/<int:pk>/update/', views.CarUpdateView.as_view(), name='car_update'),
    path('cars/<int:pk>/delete/', views.CarDeleteView.as_view(), name='car_delete'),
]
