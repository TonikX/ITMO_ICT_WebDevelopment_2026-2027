from django.urls import path
from . import views

urlpatterns = [
    path('', views.homework_list_view, name='homework_list'),
    path('homework/<int:homework_id>/', views.homework_detail_view, name='homework_detail'),
    path('grades/', views.grades_list_view, name='grades_list'),
    path('signup/', views.signup_view, name='signup'),
]
