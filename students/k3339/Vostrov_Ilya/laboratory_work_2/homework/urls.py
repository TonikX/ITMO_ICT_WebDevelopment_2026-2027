"""Маршруты приложения "Доска домашних заданий"."""

from django.urls import path

from . import views

app_name = 'homework'

urlpatterns = [
    path('', views.index, name='index'),
    path('homework/<int:pk>/', views.homework_detail, name='homework_detail'),
    path('my/', views.my_submissions, name='my_submissions'),
    path('summary/', views.class_summary, name='class_summary'),
    path('register/', views.register, name='register'),
]
