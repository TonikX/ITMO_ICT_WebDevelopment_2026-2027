
from django.urls import path
from .views import WarriorAPIView, ProfessionCreateView, SkillListView, SkillCreateView, WarriorListAPIView, ProfessionCreateAPIView, WarriorProfessionListAPIView, WarriorSkillsListAPIView, WarriorDetailAPIView, WarriorDeleteAPIView, WarriorUpdateAPIView

app_name = "warriors_app"

urlpatterns = [
    path('warriors/', WarriorAPIView.as_view()),
    path('profession/create/', ProfessionCreateView.as_view()),
    path('skills/', SkillListView.as_view()),
    path('skill/create/', SkillCreateView.as_view()),
    path('warriors/list/', WarriorListAPIView.as_view()),
    path('profession/generic_create/', ProfessionCreateAPIView.as_view()),
    path('warriors/professions/', WarriorProfessionListAPIView.as_view()),
    path('warriors/skills/', WarriorSkillsListAPIView.as_view()),
    path('warriors/detail/<int:pk>/', WarriorDetailAPIView.as_view()),
    path('warriors/delete/<int:pk>/', WarriorDeleteAPIView.as_view()),
    path('warriors/update/<int:pk>/', WarriorUpdateAPIView.as_view()),
]
