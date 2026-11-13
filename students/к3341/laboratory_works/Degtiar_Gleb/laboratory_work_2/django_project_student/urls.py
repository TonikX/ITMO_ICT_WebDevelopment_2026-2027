from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path, include
from accounts.views import register, sign_out
urlpatterns=[path('admin/',admin.site.urls),path('accounts/register/',register,name='register'),
 path('accounts/login/',LoginView.as_view(template_name='login.html'),name='login'),
 path('accounts/logout/',sign_out,name='logout'),path('',include('tours.urls')),
 path('practice/',include('project_first_app.urls'))]
