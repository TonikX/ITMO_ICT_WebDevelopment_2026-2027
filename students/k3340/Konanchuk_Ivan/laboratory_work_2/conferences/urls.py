from django.urls import path

from . import views

urlpatterns = [
    path("", views.ConferenceListView.as_view(), name="conference_list"),
    path("conference/<int:pk>/", views.ConferenceDetailView.as_view(), name="conference_detail"),
    path("conference/<int:pk>/register/", views.ParticipationCreateView.as_view(),
         name="participation_create"),
    path("conference/<int:pk>/review/", views.ReviewCreateView.as_view(), name="review_create"),
    path("my/", views.MyParticipationListView.as_view(), name="my_participations"),
    path("participation/<int:pk>/edit/", views.ParticipationUpdateView.as_view(),
         name="participation_update"),
    path("participation/<int:pk>/delete/", views.ParticipationDeleteView.as_view(),
         name="participation_delete"),
    path("participation/<int:pk>/result/", views.set_result, name="set_result"),
    path("participants/", views.ParticipantListView.as_view(), name="participant_list"),
    path("review/<int:pk>/delete/", views.ReviewDeleteView.as_view(), name="review_delete"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
]
