from django.urls import path

from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='list'),
    path('task/<int:pk>/', views.task_detail, name='task'),
    path('mine/', views.my_works, name='mine'),
    path('stats/', views.class_stats, name='stats'),
    path('signup/', views.signup, name='signup'),
]
