from django.db import transaction
from rest_framework import serializers

from .models import Profession, Skill, SkillOfWarrior, Warrior


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = ("id", "title", "description")


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "title")


class SkillAssignmentReadSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = SkillOfWarrior
        fields = ("skill", "level")


class WarriorWithProfessionSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    race_display = serializers.CharField(source="get_race_display", read_only=True)

    class Meta:
        model = Warrior
        fields = ("id", "name", "race", "race_display", "level", "profession")


class WarriorWithSkillsSerializer(serializers.ModelSerializer):
    skills = SkillAssignmentReadSerializer(
        source="skill_assignments",
        many=True,
        read_only=True,
    )
    race_display = serializers.CharField(source="get_race_display", read_only=True)

    class Meta:
        model = Warrior
        fields = ("id", "name", "race", "race_display", "level", "skills")


class WarriorDetailSerializer(serializers.ModelSerializer):
    profession = ProfessionSerializer(read_only=True)
    skills = SkillAssignmentReadSerializer(
        source="skill_assignments",
        many=True,
        read_only=True,
    )
    race_display = serializers.CharField(source="get_race_display", read_only=True)

    class Meta:
        model = Warrior
        fields = (
            "id",
            "name",
            "race",
            "race_display",
            "level",
            "profession",
            "skills",
        )


class SkillAssignmentInputSerializer(serializers.Serializer):
    skill = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all())
    level = serializers.IntegerField(min_value=0)


class WarriorWriteSerializer(serializers.ModelSerializer):
    profession = serializers.PrimaryKeyRelatedField(
        queryset=Profession.objects.all(),
        allow_null=True,
        required=False,
    )
    skills = SkillAssignmentInputSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = Warrior
        fields = ("id", "name", "race", "level", "profession", "skills")
        read_only_fields = ("id",)

    def validate_skills(self, value):
        skill_ids = [item["skill"].pk for item in value]
        if len(skill_ids) != len(set(skill_ids)):
            raise serializers.ValidationError("Одно умение нельзя указать дважды.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        skill_assignments = validated_data.pop("skills", [])
        warrior = Warrior.objects.create(**validated_data)
        self.replace_skills(warrior, skill_assignments)
        return warrior

    @transaction.atomic
    def update(self, instance, validated_data):
        skill_assignments = validated_data.pop("skills", None)
        if "profession" not in validated_data:
            validated_data["profession"] = None
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if skill_assignments is None:
            skill_assignments = []
        self.replace_skills(instance, skill_assignments)
        return instance

    @staticmethod
    def replace_skills(warrior, skill_assignments):
        SkillOfWarrior.objects.filter(warrior=warrior).delete()
        SkillOfWarrior.objects.bulk_create(
            [
                SkillOfWarrior(
                    warrior=warrior,
                    skill=item["skill"],
                    level=item["level"],
                )
                for item in skill_assignments
            ]
        )

    def to_representation(self, instance):
        return WarriorDetailSerializer(instance, context=self.context).data
