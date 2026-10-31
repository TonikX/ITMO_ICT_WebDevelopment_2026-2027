from django.urls import path

from . import views

urlpatterns = [
    path('', views.owner_list, name='owner_list'),
    path('owner/<int:owner_id>/', views.owner_detail, name='owner_detail'),
    path('owner/create/', views.owner_create, name='owner_create'),
    path('cars/', views.CarList.as_view(), name='car_list'),
    path('cars/<int:pk>/', views.CarDetail.as_view(), name='car_detail'),
    path('cars/create/', views.CarCreate.as_view(), name='car_create'),
    path('cars/<int:pk>/update/', views.CarUpdate.as_view(), name='car_update'),
    path('cars/<int:pk>/delete/', views.CarDelete.as_view(), name='car_delete'),
]
