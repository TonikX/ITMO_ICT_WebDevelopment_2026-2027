from django.db import models


class Profession(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()

    def __str__(self):
        return self.title


class Skill(models.Model):
    title = models.CharField(max_length=120)

    def __str__(self):
        return self.title


class Warrior(models.Model):
    RACE_TYPES = (
        ("s", "student"),
        ("d", "developer"),
        ("t", "teamlead"),
    )
    race = models.CharField(max_length=1, choices=RACE_TYPES)
    name = models.CharField(max_length=120)
    level = models.IntegerField(default=0)
    skill = models.ManyToManyField(
        "Skill",
        through="SkillOfWarrior",
        related_name="warrior_skils",
        blank=True,
    )
    profession = models.ForeignKey(
        "Profession",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="warriors",
    )

    def __str__(self):
        return self.name


class SkillOfWarrior(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    warrior = models.ForeignKey(Warrior, on_delete=models.CASCADE, related_name="warrior_skill")
    level = models.IntegerField()

    def __str__(self):
        return f"{self.warrior} — {self.skill}"
