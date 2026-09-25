from django.urls import path

from .views import (
    SkillAPIView,
    WarriorDestroyAPIView,
    WarriorProfessionListAPIView,
    WarriorRetrieveAPIView,
    WarriorSkillListAPIView,
    WarriorUpdateAPIView,
)

app_name = "warriors_app"

urlpatterns = [
    path("skills/", SkillAPIView.as_view()),
    path("warriors/profession/", WarriorProfessionListAPIView.as_view()),
    path("warriors/skill/", WarriorSkillListAPIView.as_view()),
    path("warriors/<int:pk>/", WarriorRetrieveAPIView.as_view()),
    path("warriors/<int:pk>/delete/", WarriorDestroyAPIView.as_view()),
    path("warriors/<int:pk>/update/", WarriorUpdateAPIView.as_view()),
]
