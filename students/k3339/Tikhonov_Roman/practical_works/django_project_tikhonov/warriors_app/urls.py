from django.urls import path

from . import views

app_name = "warriors_app"

urlpatterns = [
    path("warriors/", views.WarriorAPIView.as_view()),
    path("warriors/list/", views.WarriorListAPIView.as_view()),
    path("warriors/professions/", views.WarriorProfessionsListAPIView.as_view()),
    path("warriors/skills/", views.WarriorSkillsListAPIView.as_view()),
    path("warrior/<int:pk>/", views.WarriorDetailAPIView.as_view()),
    path("warrior/<int:pk>/update/", views.WarriorUpdateAPIView.as_view()),
    path("warrior/<int:pk>/delete/", views.WarriorDeleteAPIView.as_view()),
    path("profession/create/", views.ProfessionCreateView.as_view()),
    path("skills/", views.SkillAPIView.as_view()),
]
