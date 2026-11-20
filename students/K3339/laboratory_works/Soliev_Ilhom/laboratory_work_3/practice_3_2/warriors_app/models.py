from django.db import models


class Profession(models.Model):
    title = models.CharField(max_length=120, unique=True, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")

    class Meta:
        ordering = ("title",)
        verbose_name = "профессия"
        verbose_name_plural = "профессии"

    def __str__(self):
        return self.title


class Skill(models.Model):
    title = models.CharField(max_length=120, unique=True, verbose_name="Название")

    class Meta:
        ordering = ("title",)
        verbose_name = "умение"
        verbose_name_plural = "умения"

    def __str__(self):
        return self.title


class Warrior(models.Model):
    RACE_TYPES = (
        ("h", "Human"),
        ("a", "Asgardian"),
        ("m", "Mutated Human"),
        ("s", "Synthetic"),
        ("k", "Kree-Human Hybrid"),
    )

    name = models.CharField(max_length=120, verbose_name="Имя")
    race = models.CharField(max_length=1, choices=RACE_TYPES, verbose_name="Species")
    level = models.PositiveIntegerField(default=0, verbose_name="Уровень")
    profession = models.ForeignKey(
        Profession,
        on_delete=models.SET_NULL,
        related_name="warriors",
        null=True,
        blank=True,
        verbose_name="Профессия",
    )
    skills = models.ManyToManyField(
        Skill,
        through="SkillOfWarrior",
        related_name="warriors",
        verbose_name="Умения",
    )

    class Meta:
        ordering = ("name", "id")
        verbose_name = "воин"
        verbose_name_plural = "воины"

    def __str__(self):
        return self.name


class SkillOfWarrior(models.Model):
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="warrior_assignments",
        verbose_name="Умение",
    )
    warrior = models.ForeignKey(
        Warrior,
        on_delete=models.CASCADE,
        related_name="skill_assignments",
        verbose_name="Воин",
    )
    level = models.PositiveIntegerField(verbose_name="Уровень владения умением")

    class Meta:
        ordering = ("warrior_id", "skill_id")
        constraints = [
            models.UniqueConstraint(
                fields=("warrior", "skill"),
                name="unique_skill_per_warrior",
            )
        ]
        verbose_name = "умение воина"
        verbose_name_plural = "умения воинов"

    def __str__(self):
        return "{} — {} ({})".format(self.warrior, self.skill, self.level)
