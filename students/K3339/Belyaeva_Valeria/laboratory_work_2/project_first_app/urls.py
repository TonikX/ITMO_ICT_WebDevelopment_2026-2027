from django.urls import path
from . import views

urlpatterns = [path('', views.owners, name='owner_list'), path('owners/new/', views.owner_create, name='owner_create'),
               path('owners/<int:pk>/', views.owner_detail, name='owner_detail'),
               path('cars/', views.CarList.as_view(), name='car_list'),
               path('cars/new/', views.CarCreate.as_view(), name='car_create'),
               path('cars/<int:pk>/', views.CarDetail.as_view(), name='car_detail'),
               path('cars/<int:pk>/edit/', views.CarUpdate.as_view(), name='car_update'),
               path('cars/<int:pk>/delete/', views.CarDelete.as_view(), name='car_delete')]
