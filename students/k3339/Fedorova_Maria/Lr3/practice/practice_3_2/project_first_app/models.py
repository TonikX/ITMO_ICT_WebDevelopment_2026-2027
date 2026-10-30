from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Profession(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.title


class Warrior(models.Model):
    race = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    level = models.PositiveIntegerField(default=1)
    profession = models.ForeignKey(
        Profession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warriors",
    )
    skills = models.ManyToManyField(
        Skill,
        through="SkillOfWarrior",
        related_name="warriors",
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.race})"


class SkillOfWarrior(models.Model):
    warrior = models.ForeignKey(
        Warrior,
        on_delete=models.CASCADE,
        related_name="skill_links",
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="warrior_links",
    )
    level = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("warrior", "skill")

    def __str__(self) -> str:
        return f"{self.warrior} — {self.skill} ({self.level})"
