from django.urls import path
from . import views

urlpatterns = [
    path('', views.race_list, name='race_list'),
    path('races/<int:pk>/', views.race_detail, name='race_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('registrations/', views.my_registrations, name='my_registrations'),
    path('races/<int:pk>/register/', views.registration_create, name='registration_create'),
    path('registrations/<int:pk>/edit/', views.registration_edit, name='registration_edit'),
    path('registrations/<int:pk>/delete/', views.registration_delete, name='registration_delete'),
    path('races/<int:pk>/comment/', views.comment_create, name='comment_create'),
    path('registrations/<int:pk>/result/', views.result_edit, name='result_edit'),
]
