from rest_framework import serializers

from .models import Profession, Skill, Warrior


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = "__all__"


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class SkillCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)

    def create(self, validated_data):
        return Skill.objects.create(**validated_data)


class WarriorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warrior
        fields = "__all__"


class WarriorProfessionSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)

    class Meta:
        model = Warrior
        fields = "__all__"


class WarriorSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Warrior
        fields = "__all__"


class WarriorFullSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    skill = SkillSerializer(many=True, read_only=True)
    race = serializers.CharField(source="get_race_display", read_only=True)

    class Meta:
        model = Warrior
        fields = "__all__"
