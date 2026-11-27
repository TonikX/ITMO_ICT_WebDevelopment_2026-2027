from django.db import models

class RaceChoices(models.TextChoices):
    ORC = 'o', 'Орк'
    ELF = 'e', 'Эльф'
    HUMAN = 'h', 'Человек'

class Profession(models.Model):
    title = models.CharField('Название', max_length=120)
    description = models.TextField('Описание')

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

class Skill(models.Model):
    title = models.CharField('Название', max_length=120)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

class Warrior(models.Model):
    race = models.CharField('Раса', max_length=1, choices=RaceChoices.choices, default='h')
    name = models.CharField('Имя', max_length=120)
    level = models.PositiveIntegerField('Уровень', default=0)
    profession = models.ForeignKey(
        Profession, on_delete=models.CASCADE, related_name='warriors', verbose_name='Профессия',
    )
    skills = models.ManyToManyField(
        Skill, through='SkillOfWarrior', related_name='warriors', verbose_name='Скилы',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} (ур. {self.level})'

class SkillOfWarrior(models.Model):
    LEVEL_CHOICES = [(i, str(i)) for i in range(1, 11)]

    warrior = models.ForeignKey(
        Warrior, on_delete=models.CASCADE, related_name='skill_ranks', verbose_name='Воин',
    )
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name='warrior_ranks', verbose_name='Скил',
    )
    level = models.PositiveIntegerField('Уровень скила', choices=LEVEL_CHOICES, default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['warrior', 'skill'], name='unique_warrior_skill'),
        ]

    def __str__(self):
        return f'{self.warrior.name}: {self.skill.title} ур. {self.level}'
