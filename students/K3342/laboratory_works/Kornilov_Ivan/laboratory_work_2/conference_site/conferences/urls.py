from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.ConferenceListView.as_view(), name='conference_list'),
    path('conferences/<int:pk>/', views.conference_detail, name='conference_detail'),
    path('conferences/<int:conference_id>/talk/', views.talk_create, name='talk_create'),
    path('conferences/<int:conference_id>/review/', views.review_create, name='review_create'),
    path('talks/', views.MyTalkListView.as_view(), name='my_talks'),
    path('talks/<int:pk>/edit/', views.talk_edit, name='talk_edit'),
    path('talks/<int:pk>/delete/', views.talk_delete, name='talk_delete'),
    path('participants/', views.ParticipantListView.as_view(), name='participants'),
    path('talks/<int:pk>/publication/', views.set_publication, name='set_publication'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
]
