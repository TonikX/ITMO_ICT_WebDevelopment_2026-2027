
from django.urls import path

from . import views

urlpatterns = [
    path('', views.people_list, name='people_list'),
    path('register/', views.register, name='register'),
    path('owner/<int:pk>/', views.owner, name='owner'),
    path('cars/', views.CarListView.as_view(), name='car_list'),
]
