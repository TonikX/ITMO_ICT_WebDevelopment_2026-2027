from django.core.management.base import BaseCommand
from django.db import transaction

from warriors_app.models import Profession, Skill, SkillOfWarrior, Warrior


class Command(BaseCommand):
    help = "Создать тестовые профессии, навыки и пять воинов без дубликатов."

    @transaction.atomic
    def handle(self, *args, **options):
        professions = []
        for title, description in [
            ("Backend-разработчик", "Разрабатывает серверную часть приложения."),
            ("Frontend-разработчик", "Создаёт интерфейсы веб-приложений."),
            ("Тестировщик", "Проверяет качество программного обеспечения."),
            ("Руководитель команды", "Организует работу команды разработчиков."),
        ]:
            profession, _ = Profession.objects.get_or_create(
                title=title, defaults={"description": description}
            )
            professions.append(profession)

        skills = []
        for title in ["Python", "Django", "SQL", "JavaScript", "Тестирование", "Планирование"]:
            skill, _ = Skill.objects.get_or_create(title=title)
            skills.append(skill)

        for name, race, level, profession_index, skill_indices in [
            ("Мария", "student", 2, 0, [0, 1, 2]),
            ("Алексей", "developer", 5, 1, [2, 3, 4]),
            ("Анна", "developer", 4, 2, [0, 2, 4]),
            ("Иван", "teamlead", 8, 3, [0, 1, 5]),
            ("Елена", "student", 3, 0, [0, 2, 3]),
        ]:
            warrior, _ = Warrior.objects.get_or_create(
                name=name,
                defaults={"race": race, "level": level, "profession": professions[profession_index]},
            )
            for skill_level, skill_index in enumerate(skill_indices, start=1):
                SkillOfWarrior.objects.get_or_create(
                    warrior=warrior, skill=skills[skill_index], defaults={"level": skill_level}
                )
        self.stdout.write(self.style.SUCCESS("Тестовые данные созданы; существующие записи сохранены."))
