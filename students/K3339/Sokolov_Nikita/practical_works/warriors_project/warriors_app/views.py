from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Skill, Warrior
from .serializers import (
    SkillCreateSerializer,
    SkillSerializer,
    WarriorFullSerializer,
    WarriorProfessionSerializer,
    WarriorSerializer,
    WarriorSkillSerializer,
)


class SkillAPIView(APIView):
    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return Response({"Skills": serializer.data})

    def post(self, request):
        skill = request.data.get("skill", request.data)
        serializer = SkillCreateSerializer(data=skill)
        if serializer.is_valid(raise_exception=True):
            skill_saved = serializer.save()
        return Response({"Success": f"Skill '{skill_saved.title}' created succesfully."})


class WarriorProfessionListAPIView(generics.ListAPIView):
    serializer_class = WarriorProfessionSerializer
    queryset = Warrior.objects.select_related("profession").all()


class WarriorSkillListAPIView(generics.ListAPIView):
    serializer_class = WarriorSkillSerializer
    queryset = Warrior.objects.prefetch_related("skill").all()


class WarriorRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = WarriorFullSerializer
    queryset = Warrior.objects.select_related("profession").prefetch_related("skill").all()


class WarriorDestroyAPIView(generics.DestroyAPIView):
    serializer_class = WarriorSerializer
    queryset = Warrior.objects.all()


class WarriorUpdateAPIView(generics.UpdateAPIView):
    serializer_class = WarriorSerializer
    queryset = Warrior.objects.all()
