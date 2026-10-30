from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Skill, Warrior
from .serializers import (
    SkillSerializer,
    WarriorDetailSerializer,
    WarriorProfessionSerializer,
    WarriorSkillsSerializer,
    WarriorUpdateSerializer,
)


class SkillListAPIView(APIView):
    def get(self, request):
        serializer = SkillSerializer(Skill.objects.order_by("id"), many=True)
        return Response(serializer.data)


class SkillCreateAPIView(APIView):
    def post(self, request):
        serializer = SkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WarriorProfessionListAPIView(generics.ListAPIView):
    queryset = Warrior.objects.select_related("profession").order_by("id")
    serializer_class = WarriorProfessionSerializer


class WarriorSkillsListAPIView(generics.ListAPIView):
    queryset = Warrior.objects.prefetch_related("warrior_skills__skill").order_by("id")
    serializer_class = WarriorSkillsSerializer


class WarriorRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Warrior.objects.select_related("profession").prefetch_related("warrior_skills__skill")
    serializer_class = WarriorDetailSerializer


class WarriorDestroyAPIView(generics.DestroyAPIView):
    queryset = Warrior.objects.all()
    serializer_class = WarriorDetailSerializer


class WarriorUpdateAPIView(generics.UpdateAPIView):
    queryset = Warrior.objects.all()
    serializer_class = WarriorUpdateSerializer
