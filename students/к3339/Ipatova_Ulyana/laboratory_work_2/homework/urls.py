from django.urls import path
from . import views


app_name = 'homework'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('homeworks/', views.homeworks, name='homeworks'),
    path('homeworks/<int:pk>/', views.homework_detail, name='homework_detail'),
    path('teacher/', views.teacher, name='teacher'),
    path('teacher/homeworks/create/', views.teacher_homework_form, name='teacher_homework_create'),
    path('teacher/homeworks/<int:pk>/edit/', views.teacher_homework_form, name='teacher_homework_edit'),
    path('teacher/homeworks/<int:pk>/submissions/', views.teacher_submissions, name='teacher_submissions'),
    path('teacher/submissions/<int:pk>/grade/', views.teacher_grade, name='teacher_grade'),
    path('grades/', views.grades, name='grades'),
]
