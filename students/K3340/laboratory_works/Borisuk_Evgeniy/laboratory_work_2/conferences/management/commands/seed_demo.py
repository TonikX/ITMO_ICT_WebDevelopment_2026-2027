"""Учебные данные для демонстрации конференций и практик."""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from conferences.models import Conference, Topic
from project_first_app.models import Car, DriverLicense, Ownership, User


class Command(BaseCommand):
    """Создаёт повторяемый набор данных без действующих паролей."""

    help = "Добавить учебные конференции, двух владельцев и четыре автомобиля."

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        topic, _ = Topic.objects.get_or_create(name="Информатика")
        titles = [
            "Распределённые системы",
            "Прикладное машинное обучение",
            "Информационная безопасность",
            "Современные базы данных",
            "Компьютерные сети",
            "Инженерия программного обеспечения",
            "Анализ данных",
            "Человеко-компьютерное взаимодействие",
        ]
        for index, title in enumerate(titles):
            conference, created = Conference.objects.get_or_create(
                title=title,
                defaults={
                    "location": "Санкт-Петербург, университетский кампус",
                    "start_date": date(2026, 11, index + 10),
                    "end_date": date(2026, 11, index + 11),
                    "description": f"Научная конференция «{title}»: исследования, доклады и обсуждение результатов.",
                    "venue_description": "Конференц-зал университета. Доступны проектор и зона обсуждений.",
                    "participation_terms": "Зарегистрируйте тему выступления и аннотацию. Участие бесплатное.",
                },
            )
            if created:
                conference.topics.add(topic)
        owners = []
        for index, (first_name, last_name) in enumerate(
            [("Иван", "Петров"), ("Анна", "Смирнова")]
        ):
            owner, created = User.objects.get_or_create(
                username=f"demo_owner_{index + 1}",
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "birth_date": date(2000, 1, index + 1),
                    "passport_number": f"000000000{index}",
                    "address": "Вымышленный учебный адрес",
                    "nationality": "Не указана",
                },
            )
            if created:
                owner.set_unusable_password()
                owner.save(update_fields=["password"])
            DriverLicense.objects.get_or_create(
                number=f"000000000{index}",
                defaults={
                    "owner": owner,
                    "category": "B",
                    "issue_date": date(2020, 1, 1),
                },
            )
            owners.append(owner)
        cars = []
        for index in range(4):
            car, _ = Car.objects.get_or_create(
                plate_number=f"DEMO00{index + 1}",
                defaults={
                    "brand": "Lada",
                    "model_name": ["Vesta", "Granta", "Niva", "Largus"][index],
                    "color": "Белый",
                },
            )
            cars.append(car)
        for owner, selected, start, end in [
            (owners[0], cars[:3], date(2023, 1, 1), date(2024, 12, 31)),
            (owners[1], cars[1:], date(2025, 1, 1), None),
        ]:
            for car in selected:
                if not Ownership.objects.filter(
                    owner=owner, car=car, start_date=start
                ).exists():
                    ownership = Ownership(
                        owner=owner, car=car, start_date=start, end_date=end
                    )
                    ownership.full_clean()
                    ownership.save()
        self.stdout.write(
            self.style.SUCCESS("Учебные данные готовы. Пароли владельцев не заданы.")
        )
