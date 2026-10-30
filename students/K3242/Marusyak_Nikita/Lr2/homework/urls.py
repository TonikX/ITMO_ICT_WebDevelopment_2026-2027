
from django.urls import path
from . import views

urlpatterns = [
    path("", views.assignment_list, name="home"),

    path(
        "signup/",
        views.signup_view,
        name="signup"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "assignments/create/",
        views.assignment_create,
        name="assignment_create"
    ),

    path(
        "assignments/<int:pk>/edit/",
        views.assignment_edit,
        name="assignment_edit"
    ),

    path(
        "assignments/<int:pk>/",
        views.assignment_detail,
        name="assignment_detail"
    ),

    path(
        "submissions/<int:pk>/grade/",
        views.grade_submission,
        name="grade_submission"
    ),

    path(
        "grades/",
        views.gradebook,
        name="gradebook"
    ),
]
