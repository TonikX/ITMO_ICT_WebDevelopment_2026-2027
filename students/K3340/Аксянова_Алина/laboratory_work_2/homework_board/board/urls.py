
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.homework_list, name='homework_list'),

    path('register/', views.register, name='register'),

    path(
        'login/',
        auth_views.LoginView.as_view(template_name='board/login.html'),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='homework_list'),
        name='logout'
    ),

    path(
        'homework/<int:homework_id>/submit/',
        views.submit_homework,
        name='submit_homework'
    ),

    path(
        'grades/', 
        views.grade_list, 
        name='grade_list'
    ),

    path(
        'teacher/submissions/',
        views.teacher_submissions,
        name='teacher_submissions'
    ),

    path(
        'teacher/submissions/<int:submission_id>/grade/',
        views.grade_submission,
        name='grade_submission'
    ),
]
