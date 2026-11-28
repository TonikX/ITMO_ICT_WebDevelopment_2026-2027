from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("races/", views.RaceListView.as_view(), name="race_list"),
    path("races/<int:pk>/", views.RaceDetailView.as_view(), name="race_detail"),
    path("races/<int:pk>/register/", views.RegistrationCreateView.as_view(), name="registration_create"),
    path("races/<int:pk>/comment/", views.CommentCreateView.as_view(), name="comment_create"),
    path("racers/", views.RacerListView.as_view(), name="racer_list"),
    path("profile/", views.RacerProfileView.as_view(), name="racer_profile"),
    path("my/registrations/", views.MyRegistrationsView.as_view(), name="my_registrations"),
    path("my/registrations/<int:pk>/edit/", views.RegistrationUpdateView.as_view(), name="registration_update"),
    path("my/registrations/<int:pk>/delete/", views.RegistrationDeleteView.as_view(), name="registration_delete"),
]
