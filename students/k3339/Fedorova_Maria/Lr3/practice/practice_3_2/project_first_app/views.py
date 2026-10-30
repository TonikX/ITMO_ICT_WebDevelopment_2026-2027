from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profession, Skill, Warrior
from .serializers import (
    ProfessionSerializer,
    SkillSerializer,
    WarriorCreateSerializer,
    WarriorSerializer,
)


class WarriorListCreateView(generics.ListCreateAPIView):
    queryset = Warrior.objects.select_related("profession").prefetch_related(
        "skill_links__skill",
    )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return WarriorCreateSerializer
        return WarriorSerializer


class WarriorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warrior.objects.select_related("profession").prefetch_related(
        "skill_links__skill",
    )
    serializer_class = WarriorSerializer


class SkillListCreateView(generics.ListCreateAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class ProfessionListCreateView(generics.ListCreateAPIView):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer


class RelatedNameDemoView(APIView):
    def get(self, request):
        warriors_of_skills = {
            skill.name: [warrior.name for warrior in skill.warriors.all()]
            for skill in Skill.objects.prefetch_related("warriors")
        }
        professions = {
            profession.title: [
                warrior.name for warrior in profession.warriors.all()
            ]
            for profession in Profession.objects.prefetch_related("warriors")
        }
        return Response(
            {
                "skills_to_warriors": warriors_of_skills,
                "professions_to_warriors": professions,
            }
        )
