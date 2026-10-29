from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
urlpatterns = [
    path('', views.owner_list, name='owner_list'),
    path('owner/<int:pk>/', views.owner_detail, name='owner_detail'),
    path('owners/create/', views.owner_create, name='owner_create'),
    path('register/', views.registration, name='register'),
    path('login/', LoginView.as_view(template_name='form.html', extra_context={'title': 'Вход'}), name='login'),
    path('cars/', views.CarList.as_view(), name='car_list'),
    path('cars/<int:pk>/', views.CarDetail.as_view(), name='car_detail'),
    path('cars/create/', views.CarCreate.as_view(), name='car_create'),
    path('cars/<int:pk>/edit/', views.CarUpdate.as_view(), name='car_edit'),
    path('cars/<int:pk>/delete/', views.CarDelete.as_view(), name='car_delete'),
]
