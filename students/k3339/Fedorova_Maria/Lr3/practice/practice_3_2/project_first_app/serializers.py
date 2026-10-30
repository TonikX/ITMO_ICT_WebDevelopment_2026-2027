from rest_framework import serializers

from .models import Profession, Skill, SkillOfWarrior, Warrior


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name")


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ("id", "title", "description")


class SkillOfWarriorSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = SkillOfWarrior
        fields = ("id", "skill", "level")


class WarriorSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    skill_links = SkillOfWarriorSerializer(many=True, read_only=True)

    class Meta:
        model = Warrior
        fields = (
            "id",
            "race",
            "name",
            "level",
            "profession",
            "skill_links",
        )


class WarriorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warrior
        fields = (
            "id",
            "race",
            "name",
            "level",
            "profession",
        )
