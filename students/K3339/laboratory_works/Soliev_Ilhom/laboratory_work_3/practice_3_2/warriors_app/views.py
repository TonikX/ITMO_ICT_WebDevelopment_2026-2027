from django.db.models import Prefetch
from rest_framework import generics, status
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profession, Skill, SkillOfWarrior, Warrior
from .serializers import (
    ProfessionSerializer,
    SkillSerializer,
    WarriorDetailSerializer,
    WarriorWithProfessionSerializer,
    WarriorWithSkillsSerializer,
    WarriorWriteSerializer,
)


class APIRootAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            {
                "skills": reverse("warriors_app:skill-list-create", request=request),
                "professions": reverse("warriors_app:profession-list-create", request=request),
                "warriors": reverse("warriors_app:warrior-list-create", request=request),
                "warriors_with_skills": reverse(
                    "warriors_app:warrior-list-skills",
                    request=request,
                ),
            }
        )


class SkillListCreateAPIView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = SkillSerializer(Skill.objects.all(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = SkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        skill = serializer.save()
        return Response(
            SkillSerializer(skill).data,
            status=status.HTTP_201_CREATED,
        )


class SkillDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    http_method_names = ["get", "put", "delete", "head", "options"]


class ProfessionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer


class ProfessionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer
    http_method_names = ["get", "put", "delete", "head", "options"]


class WarriorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Warrior.objects.select_related("profession").all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return WarriorWriteSerializer
        return WarriorWithProfessionSerializer


class WarriorWithSkillsListAPIView(generics.ListAPIView):
    serializer_class = WarriorWithSkillsSerializer

    def get_queryset(self):
        assignment_queryset = SkillOfWarrior.objects.select_related("skill")
        return Warrior.objects.prefetch_related(
            Prefetch("skill_assignments", queryset=assignment_queryset)
        )


class WarriorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WarriorWriteSerializer
    http_method_names = ["get", "put", "delete", "head", "options"]

    def get_queryset(self):
        assignment_queryset = SkillOfWarrior.objects.select_related("skill")
        return Warrior.objects.select_related("profession").prefetch_related(
            Prefetch("skill_assignments", queryset=assignment_queryset)
        )
