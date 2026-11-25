from django.urls import path
from rest_framework import generics, serializers
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Profession, Skill, SkillOfWarrior, Warrior


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "title"]


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ["id", "title", "description"]


class SkillLinkSerializer(serializers.ModelSerializer):
    skill = SkillSerializer()

    class Meta:
        model = SkillOfWarrior
        fields = ["skill", "level"]


class WarriorSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    profession_id = serializers.PrimaryKeyRelatedField(
        queryset=Profession.objects.all(), source="profession", write_only=True,
    )
    skills = SkillLinkSerializer(source="skill_links", many=True, read_only=True)

    class Meta:
        model = Warrior
        fields = ["id", "name", "race", "level", "profession", "profession_id", "skills"]


class WarriorProfessionSerializer(WarriorSerializer):
    class Meta(WarriorSerializer.Meta):
        fields = ["id", "name", "race", "level", "profession"]


class WarriorSkillsSerializer(WarriorSerializer):
    class Meta(WarriorSerializer.Meta):
        fields = ["id", "name", "race", "level", "skills"]


class SkillView(APIView):
    def get(self, request):
        return Response(SkillSerializer(Skill.objects.order_by("id"), many=True).data)

    def post(self, request):
        serializer = SkillSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class WarriorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warrior.objects.select_related("profession").prefetch_related("skill_links__skill")
    serializer_class = WarriorSerializer


class WarriorProfessions(generics.ListAPIView):
    queryset = Warrior.objects.select_related("profession").order_by("id")
    serializer_class = WarriorProfessionSerializer


class WarriorSkills(generics.ListAPIView):
    queryset = Warrior.objects.prefetch_related("skill_links__skill").order_by("id")
    serializer_class = WarriorSkillsSerializer


urlpatterns = [
    path("skills/", SkillView.as_view()),
    path("warriors/professions/", WarriorProfessions.as_view()),
    path("warriors/skills/", WarriorSkills.as_view()),
    path("warriors/<int:pk>/", WarriorDetail.as_view()),
]
