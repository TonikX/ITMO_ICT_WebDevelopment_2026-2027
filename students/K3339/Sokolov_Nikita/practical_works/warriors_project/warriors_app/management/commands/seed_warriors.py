from django.core.management.base import BaseCommand

from warriors_app.models import Profession, Skill, SkillOfWarrior, Warrior


class Command(BaseCommand):
    help = "Seed demo warriors, professions, skills"

    def handle(self, *args, **options):
        prof_dev, _ = Profession.objects.get_or_create(
            title="Backend developer",
            defaults={"description": "Серверная разработка"},
        )
        prof_tl, _ = Profession.objects.get_or_create(
            title="Teamlead",
            defaults={"description": "Руководство командой"},
        )

        java, _ = Skill.objects.get_or_create(title="Java programming")
        gaming, _ = Skill.objects.get_or_create(title="Умение играть во все подряд")
        hack, _ = Skill.objects.get_or_create(title="Взлом компьютера")

        w1, _ = Warrior.objects.get_or_create(
            name="Николай Леонтьев",
            defaults={"race": "s", "level": 20, "profession": prof_dev},
        )
        w2, _ = Warrior.objects.get_or_create(
            name="Дмитрий Мартынов",
            defaults={"race": "t", "level": 66, "profession": prof_tl},
        )
        w3, _ = Warrior.objects.get_or_create(
            name="Никита Михайловский",
            defaults={"race": "s", "level": 15, "profession": prof_dev},
        )

        for warrior, skill, level in (
            (w1, hack, 15),
            (w1, java, 10),
            (w3, gaming, 12),
            (w2, java, 40),
        ):
            SkillOfWarrior.objects.get_or_create(
                warrior=warrior,
                skill=skill,
                defaults={"level": level},
            )

        self.stdout.write(f"warriors={Warrior.objects.count()} skills={Skill.objects.count()}")
