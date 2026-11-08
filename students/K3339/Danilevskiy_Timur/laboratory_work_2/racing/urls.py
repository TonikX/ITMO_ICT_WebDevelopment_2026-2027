from django.urls import path
from django.contrib.auth.views import LoginView
from . import views
from .forms import LoginForm

urlpatterns = [
    path('', views.home, name='home'),
    path('races/', views.race_list, name='races'),
    path('races/<slug:slug>/', views.race_detail, name='race_detail'),
    path('races/<slug:slug>/enter/', views.entry_edit, name='entry_create'),
    path('races/<slug:slug>/entries/<int:pk>/edit/', views.entry_edit, name='entry_edit'),
    path('entries/<int:pk>/delete/', views.entry_delete, name='entry_delete'),
    path('races/<slug:slug>/comments/', views.comment_add, name='comment_add'),
    path('drivers/', views.drivers, name='drivers'),
    path('account/signup/', views.signup, name='signup'),
    path('account/login/', LoginView.as_view(template_name='racing/auth.html', authentication_form=LoginForm, redirect_authenticated_user=True), name='login'),
    path('account/logout/', views.signout, name='logout'),
    path('account/entries/', views.my_entries, name='my_entries'),
    path('control/', views.race_control, name='control'),
    path('control/<slug:slug>/heats/new/', views.heat_edit, name='heat_create'),
    path('control/<slug:slug>/heats/<int:pk>/', views.heat_edit, name='heat_edit'),
]
