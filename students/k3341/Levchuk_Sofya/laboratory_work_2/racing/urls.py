from django.urls import path
from . import views

urlpatterns = [
    path('', views.race_list, name='race_list'),
    path('races/create/', views.race_create, name='race_create'),
    path('races/<int:pk>/edit/', views.race_edit, name='race_edit'),
    path('races/<int:pk>/delete/', views.race_delete, name='race_delete'),
    path('registrations/<int:pk>/set-result/', views.registration_set_result, name='registration_set_result'),
    path('races/<int:pk>/', views.race_detail, name='race_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('races/<int:race_id>/register/', views.registration_create, name='registration_create'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    path('registrations/<int:pk>/edit/', views.registration_edit, name='registration_edit'),
    path('registrations/<int:pk>/delete/', views.registration_delete, name='registration_delete'),
    path('races/<int:race_id>/comment/', views.comment_create, name='comment_create'),

]