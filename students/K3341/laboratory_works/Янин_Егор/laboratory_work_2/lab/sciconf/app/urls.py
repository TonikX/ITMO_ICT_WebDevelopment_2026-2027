from django.urls import path

from . import views

urlpatterns = [
    path("", views.conference_list, name="conference_list"),
    path("participants/", views.participant_list, name="participant_list"),
    path("register/", views.register, name="register"),
    path("login/", views.StyledLoginView.as_view(), name="login"),
    path("logout/", views.RegistrationLogoutView.as_view(), name="logout"),
    path("conferences/<int:conference_id>/", views.conference_detail, name="conference_detail"),
    path("conferences/<int:conference_id>/submit/", views.submit_talk, name="submit_talk"),
    path("submissions/<int:submission_id>/edit/", views.edit_talk, name="edit_talk"),
    path("submissions/<int:submission_id>/delete/", views.delete_talk, name="delete_talk"),
]
