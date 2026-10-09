from django.contrib import admin
from django.urls import path, include
from conference_app import views as app_views


urlpatterns = [
    path('admin/', admin.site.urls),

    # Bài 2.3 — Django auth URLs có sẵn (login, logout, password change...)
    path('accounts/', include('django.contrib.auth.urls')),

    # Bài 2.3 — Đăng ký user (không có sẵn trong auth.urls)
    path('register/', app_views.register, name='register'),

    # App URLs
    path('', include('conference_app.urls')),
]