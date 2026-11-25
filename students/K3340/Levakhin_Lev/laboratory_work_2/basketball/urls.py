from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm

app_name = 'basketball'

urlpatterns = [
    path('', views.BasketballMatchListView.as_view(), name='match_list'),

    path('teams/', views.TeamListView.as_view(), name='team_list'),
    path('team/<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('match/<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),

    path('login/', auth_views.LoginView.as_view(
        template_name='basketball/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]