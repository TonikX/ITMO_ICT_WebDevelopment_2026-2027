from django.urls import path

from .views import (
    ProfessionListCreateView,
    RelatedNameDemoView,
    SkillListCreateView,
    WarriorDetailView,
    WarriorListCreateView,
)

urlpatterns = [
    path("warriors/", WarriorListCreateView.as_view()),
    path("warriors/<int:pk>/", WarriorDetailView.as_view()),
    path("skills/", SkillListCreateView.as_view()),
    path("professions/", ProfessionListCreateView.as_view()),
    path("related-demo/", RelatedNameDemoView.as_view()),
]
