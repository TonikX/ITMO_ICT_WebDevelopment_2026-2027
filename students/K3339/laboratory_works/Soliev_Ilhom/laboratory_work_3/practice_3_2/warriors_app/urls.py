from django.urls import path

from .views import (
    APIRootAPIView,
    ProfessionDetailAPIView,
    ProfessionListCreateAPIView,
    SkillDetailAPIView,
    SkillListCreateAPIView,
    WarriorDetailAPIView,
    WarriorListCreateAPIView,
    WarriorWithSkillsListAPIView,
)


app_name = "warriors_app"

urlpatterns = [
    path("", APIRootAPIView.as_view(), name="api-root"),
    path("skills/", SkillListCreateAPIView.as_view(), name="skill-list-create"),
    path("skills/<int:pk>/", SkillDetailAPIView.as_view(), name="skill-detail"),
    path("professions/", ProfessionListCreateAPIView.as_view(), name="profession-list-create"),
    path("professions/<int:pk>/", ProfessionDetailAPIView.as_view(), name="profession-detail"),
    path("warriors/", WarriorListCreateAPIView.as_view(), name="warrior-list-create"),
    path("warriors/with-skills/", WarriorWithSkillsListAPIView.as_view(), name="warrior-list-skills"),
    path("warriors/<int:pk>/", WarriorDetailAPIView.as_view(), name="warrior-detail"),
]
