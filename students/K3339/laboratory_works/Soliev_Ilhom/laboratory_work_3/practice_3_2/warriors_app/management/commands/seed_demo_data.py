from django.core.management.base import BaseCommand

from warriors_app.models import Profession, Skill, SkillOfWarrior, Warrior


PROFESSIONS = (
    ("Avenger", "A member of Earth's premier superhero team."),
    ("S.H.I.E.L.D. Agent", "A highly trained agent protecting Earth."),
    ("Master of the Mystic Arts", "A guardian trained in powerful mystical arts."),
    ("Wakandan Hero", "A protector of Wakanda and its people."),
)

SKILLS = (
    "Powered Armor",
    "Genius Intellect",
    "Shield Mastery",
    "Super Soldier Strength",
    "Asgardian Strength",
    "Lightning Control",
    "Stealth",
    "Martial Arts",
    "Marksmanship",
    "Web-Slinging",
    "Spider-Sense",
    "Gamma Strength",
    "Durability",
    "Spell Casting",
    "Portal Magic",
    "Vibranium Technology",
    "Enhanced Agility",
    "Flight",
    "Energy Projection",
    "Intangibility",
    "Leadership",
)

WARRIORS = (
    (
        "Tony Stark",
        "h",
        91,
        "Avenger",
        (("Powered Armor", 98), ("Genius Intellect", 100), ("Flight", 85)),
    ),
    (
        "Steve Rogers",
        "h",
        95,
        "Avenger",
        (("Super Soldier Strength", 95), ("Shield Mastery", 100), ("Leadership", 92)),
    ),
    (
        "Thor Odinson",
        "a",
        100,
        "Avenger",
        (("Asgardian Strength", 100), ("Lightning Control", 96)),
    ),
    (
        "Natasha Romanoff",
        "h",
        84,
        "S.H.I.E.L.D. Agent",
        (("Stealth", 98), ("Martial Arts", 94), ("Marksmanship", 91)),
    ),
    (
        "Peter Parker",
        "m",
        72,
        "Avenger",
        (("Spider-Sense", 94), ("Web-Slinging", 90), ("Enhanced Agility", 92)),
    ),
    (
        "Bruce Banner",
        "m",
        88,
        "Avenger",
        (("Gamma Strength", 99), ("Durability", 97), ("Genius Intellect", 93)),
    ),
    (
        "Stephen Strange",
        "h",
        93,
        "Master of the Mystic Arts",
        (("Spell Casting", 99), ("Portal Magic", 96)),
    ),
    (
        "Shuri",
        "h",
        86,
        "Wakandan Hero",
        (("Vibranium Technology", 98), ("Martial Arts", 82), ("Genius Intellect", 94)),
    ),
    (
        "Vision",
        "s",
        94,
        "Avenger",
        (("Flight", 90), ("Energy Projection", 96), ("Intangibility", 95)),
    ),
    (
        "Carol Danvers",
        "k",
        100,
        "Avenger",
        (("Flight", 98), ("Energy Projection", 99), ("Super Soldier Strength", 92)),
    ),
)


class Command(BaseCommand):
    help = "Creates English-language Marvel hero demo data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all practice 3.2 data before adding the demo records.",
        )

    def handle(self, *args, reset=False, **options):
        if reset:
            SkillOfWarrior.objects.all().delete()
            Warrior.objects.all().delete()
            Skill.objects.all().delete()
            Profession.objects.all().delete()

        professions = {}
        for title, description in PROFESSIONS:
            profession, _ = Profession.objects.update_or_create(
                title=title,
                defaults={"description": description},
            )
            professions[title] = profession

        skills = {}
        for title in SKILLS:
            skill, _ = Skill.objects.get_or_create(title=title)
            skills[title] = skill

        for name, race, level, profession_title, assigned_skills in WARRIORS:
            warrior, _ = Warrior.objects.update_or_create(
                name=name,
                defaults={
                    "race": race,
                    "level": level,
                    "profession": professions[profession_title],
                },
            )
            for skill_title, skill_level in assigned_skills:
                SkillOfWarrior.objects.update_or_create(
                    warrior=warrior,
                    skill=skills[skill_title],
                    defaults={"level": skill_level},
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Marvel demo data ready: {} professions, {} skills, {} heroes.".format(
                    Profession.objects.count(), Skill.objects.count(), Warrior.objects.count()
                )
            )
        )
