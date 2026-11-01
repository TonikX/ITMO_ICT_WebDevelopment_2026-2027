from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.ConferenceListView.as_view(), name="conference-list"),
    path("conferences/new/", views.ConferenceCreateView.as_view(), name="conference-create"),
    path("conferences/<int:pk>/", views.ConferenceDetailView.as_view(), name="conference-detail"),
    path("conferences/<int:pk>/edit/", views.ConferenceUpdateView.as_view(), name="conference-update"),
    path("conferences/<int:pk>/delete/", views.ConferenceDeleteView.as_view(), name="conference-delete"),
    path(
        "conferences/<int:conference_id>/register/",
        views.ParticipationCreateView.as_view(),
        name="participation-create",
    ),
    path(
        "conferences/<int:conference_id>/review/",
        views.ReviewCreateView.as_view(),
        name="review-create",
    ),
    path("participations/", views.MyParticipationsView.as_view(), name="my-participations"),
    path("participations/<int:pk>/edit/", views.ParticipationUpdateView.as_view(), name="participation-update"),
    path("participations/<int:pk>/delete/", views.ParticipationDeleteView.as_view(), name="participation-delete"),
    path("participations/<int:pk>/result/", views.ParticipationResultView.as_view(), name="participation-result"),
    path("participants/", views.ParticipantsView.as_view(), name="participants"),
    path("reviews/<int:pk>/delete/", views.ReviewDeleteView.as_view(), name="review-delete"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="conferences/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
