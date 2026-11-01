from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.RaceListView.as_view(), name='race_list'),
    path('race/<int:pk>/', views.RaceDetailView.as_view(), name='race_detail'),

    path('race/<int:pk>/enroll/', views.RaceEnrollView.as_view(), name='race_enroll'),

    path('race/<int:pk>/comment/', views.CommentCreateView.as_view(), name='race_comment'),

    # авторизация
    path('login/', LoginView.as_view(template_name='racing_board/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='race_list'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
]