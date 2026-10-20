from django.urls import path

from .views import (
    ProfessionCreateAPIView,
    ProfessionCreateView,
    SkillAPIView,
    SkillCreateView,
    SkillRelatedListAPIView,
    WarriorAPIView,
    WarriorCreateAPIView,
    WarriorDepthListAPIView,
    WarriorDestroyAPIView,
    WarriorListAPIView,
    WarriorProfessionListAPIView,
    WarriorRelatedListAPIView,
    WarriorRetrieveAPIView,
    WarriorSkillsListAPIView,
    WarriorUpdateAPIView,
)

app_name = "warriors_app"

urlpatterns = [
    path('warriors/', WarriorAPIView.as_view()),
    path('profession/create/', ProfessionCreateView.as_view()),
    path('warriors/list/', WarriorListAPIView.as_view()),
    path('profession/generic_create/', ProfessionCreateAPIView.as_view()),
    path('warrior/create/', WarriorCreateAPIView.as_view()),
    path('warriors/related/', WarriorRelatedListAPIView.as_view()),
    path('warriors/depth/', WarriorDepthListAPIView.as_view()),
    path('skills/related/', SkillRelatedListAPIView.as_view()),
    # Практическое задание 1
    path('skills/', SkillAPIView.as_view()),
    path('skill/create/', SkillCreateView.as_view()),
    # Практическое задание 2
    path('warriors/professions/', WarriorProfessionListAPIView.as_view()),
    path('warriors/skills/', WarriorSkillsListAPIView.as_view()),
    path('warrior/<int:pk>/', WarriorRetrieveAPIView.as_view()),
    path('warrior/<int:pk>/delete/', WarriorDestroyAPIView.as_view()),
    path('warrior/<int:pk>/update/', WarriorUpdateAPIView.as_view()),
]
