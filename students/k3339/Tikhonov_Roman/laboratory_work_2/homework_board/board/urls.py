from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.homework_list, name="homework_list"),
    path("homework/create/", views.homework_create, name="homework_create"),
    path("homework/<int:pk>/", views.homework_detail, name="homework_detail"),
    path("homework/<int:pk>/submissions/", views.homework_submissions, name="homework_submissions"),
    path("submissions/<int:pk>/grade/", views.submission_grade, name="submission_grade"),
    path("grades/", views.grades, name="grades"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
]
