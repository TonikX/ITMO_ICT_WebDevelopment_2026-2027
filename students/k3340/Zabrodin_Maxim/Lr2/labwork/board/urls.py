from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("", views.homework_list, name="homework_list"),
    path("register/", views.register, name="register"),
    path("login/", LoginView.as_view(template_name="login.html"), name="login",),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("homework/<int:homework_id>/answer/", views.answer_submit, name="answer_submit",),
    path("grades/", views.grade_table, name="grade_table"),
    path("homework/create/", views.homework_create, name="homework_create"),
]