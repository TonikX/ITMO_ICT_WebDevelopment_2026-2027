from django.db import models


class Profession(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class Skill(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Warrior(models.Model):
    RACES = [
        ("student", "Студент"),
        ("developer", "Разработчик"),
        ("teamlead", "Тимлид"),
    ]
    race = models.CharField(max_length=20, choices=RACES)
    name = models.CharField(max_length=100)
    level = models.PositiveIntegerField()
    skill = models.ManyToManyField(Skill, through="SkillOfWarrior", related_name="warriors")
    profession = models.ForeignKey(
        Profession, on_delete=models.SET_NULL, null=True, blank=True, related_name="warriors"
    )

    def __str__(self):
        return self.name


class SkillOfWarrior(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="warrior_skills")
    warrior = models.ForeignKey(Warrior, on_delete=models.CASCADE, related_name="warrior_skills")
    level = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.warrior}: {self.skill} (уровень {self.level})"
