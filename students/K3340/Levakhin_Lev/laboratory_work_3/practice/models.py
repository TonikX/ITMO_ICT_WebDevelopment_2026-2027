from django.db import models


class Car(models.Model):
    brand = models.CharField(max_length=40)
    model = models.CharField(max_length=60)
    color = models.CharField(max_length=40)


class Owner(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    passport_number = models.CharField(max_length=20, unique=True)
    cars = models.ManyToManyField(Car, through="Ownership", related_name="owners")


class License(models.Model):
    owner = models.OneToOneField(Owner, models.CASCADE, related_name="license")
    number = models.CharField(max_length=20, unique=True)
    issued_on = models.DateField()


class Ownership(models.Model):
    owner = models.ForeignKey(Owner, models.CASCADE, related_name="ownerships")
    car = models.ForeignKey(Car, models.CASCADE, related_name="ownerships")
    started_on = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["owner", "car", "started_on"], name="practice_ownership_unique"),
        ]


class Skill(models.Model):
    title = models.CharField(max_length=80, unique=True)


class Profession(models.Model):
    title = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)


class Warrior(models.Model):
    name = models.CharField(max_length=80)
    race = models.CharField(max_length=40)
    level = models.PositiveIntegerField(default=1)
    profession = models.ForeignKey(Profession, models.PROTECT, related_name="warriors")
    skills = models.ManyToManyField(Skill, through="SkillOfWarrior", related_name="warriors")


class SkillOfWarrior(models.Model):
    warrior = models.ForeignKey(Warrior, models.CASCADE, related_name="skill_links")
    skill = models.ForeignKey(Skill, models.CASCADE, related_name="warrior_links")
    level = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["warrior", "skill"], name="practice_warrior_skill_unique"),
        ]
