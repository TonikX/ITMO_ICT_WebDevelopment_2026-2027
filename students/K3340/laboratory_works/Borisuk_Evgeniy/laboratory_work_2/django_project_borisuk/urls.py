"""Маршруты приложения, практик и административной панели."""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from conferences.views import logout_user, signup

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/signup/", signup, name="signup"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("accounts/logout/", logout_user, name="logout"),
    path("practice/", include("project_first_app.urls")),
    path("", include("conferences.urls")),
]
