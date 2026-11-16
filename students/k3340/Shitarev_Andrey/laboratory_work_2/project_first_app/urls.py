from django.urls import path
from . import views

urlpatterns = [
    path('', views.race_list, name='race_list'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('profile/', views.driver_profile, name='profile'),
    path('registrations/', views.my_registrations, name='my_registrations'),
    path('races/new/', views.race_edit, name='race_create'),
    path('races/<int:race_id>/', views.race_detail, name='race_detail'),
    path('races/<int:race_id>/edit/', views.race_edit, name='race_edit'),
    path('races/<int:race_id>/delete/', views.race_delete, name='race_delete'),
    path('races/<int:race_id>/register/', views.registration_create, name='registration_create'),
    path('races/<int:race_id>/comment/', views.comment_create, name='comment_create'),
    path('registrations/<int:pk>/edit/', views.registration_edit, name='registration_edit'),
    path('registrations/<int:pk>/delete/', views.registration_delete, name='registration_delete'),
]
