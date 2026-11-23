from django.urls import path
from . import views

urlpatterns = [
    path('owners/', views.owner_list, name='owners'),
    path('owners/new/', views.owner_create, name='owner_create'),
    path('owners/<int:pk>/', views.owner_detail, name='owner'),
    path('cars/', views.CarList.as_view(), name='cars'),
    path('cars/new/', views.CarCreate.as_view(), name='car_create'),
    path('cars/<int:pk>/', views.CarDetail.as_view(), name='car'),
    path('cars/<int:pk>/edit/', views.CarUpdate.as_view(), name='car_edit'),
    path('cars/<int:pk>/delete/', views.CarDelete.as_view(), name='car_delete'),
]
