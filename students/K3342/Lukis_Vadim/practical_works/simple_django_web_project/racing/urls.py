from django.urls import path
from . import views

urlpatterns = [
    path('owners/', views.car_owner_list, name='car_owner_list'),
    path('owners/<int:pk>/', views.car_owner_detail, name='car_owner_detail'),
    path('owners/create/', views.car_owner_create, name='car_owner_create'),
    path('owners/<int:pk>/update/', views.car_owner_update, name='car_owner_update'),
    path('owners/<int:pk>/delete/', views.car_owner_delete, name='car_owner_delete'),

    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('cars/create/', views.car_create, name='car_create'),
    path('cars/<int:pk>/update/', views.car_update, name='car_update'),
    path('cars/<int:pk>/delete/', views.car_delete, name='car_delete'),

    path('races/', views.race_list, name='race_list'),
    path('races/<int:pk>/', views.race_detail, name='race_detail'),
    path('races/<int:pk>/register/', views.race_register, name='race_register'),
    path('races/<int:pk>/unregister/', views.race_unregister, name='race_unregister'),
    path('races/<int:pk>/review/', views.review_create, name='review_create'),
    path('races/<int:pk>/results/', views.race_results, name='race_results'),

    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
