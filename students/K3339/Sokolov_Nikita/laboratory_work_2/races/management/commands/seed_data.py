from datetime import date, timedelta
import os

from django.core.management.base import BaseCommand, CommandError

from races.models import Race, RaceComment, RaceEntry, RaceResult, User


class Command(BaseCommand):
    help = "Seed demo races, users, entries, results, comments"

    def handle(self, *args, **options):
        admin_password = os.environ.get("DEMO_ADMIN_PASSWORD")
        user_password = os.environ.get("DEMO_USER_PASSWORD")
        if not admin_password or not user_password:
            raise CommandError(
                "Задайте DEMO_ADMIN_PASSWORD и DEMO_USER_PASSWORD "
                "(скопируйте .env.example в .env и заполните значения)"
            )

        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True, "email": "admin@example.com"},
        )
        if created:
            admin.set_password(admin_password)
            admin.save()

        racer, created = User.objects.get_or_create(username="racer1", defaults={"email": "racer1@example.com"})
        if created:
            racer.set_password(user_password)
            racer.save()

        racer2, created = User.objects.get_or_create(username="racer2", defaults={"email": "racer2@example.com"})
        if created:
            racer2.set_password(user_password)
            racer2.save()

        titles = [
            ("Гран-при Сочи", "Сочи Автодром", "Этап чемпионата России"),
            ("Ночной спринт Москва", "Moscow Raceway", "Короткие круги под прожекторами"),
            ("Уральский дрифт", "Екатеринбург", "Класс Pro-Am"),
            ("Балтийский кубок", "СПб, Игора Драйв", "Формула Regional"),
            ("Кавказский подъём", "Красная Поляна", "Горные заезды"),
            ("Сибирский марафон", "Новосибирск", "Выносливость 3 часа"),
            ("Крымский турбо", "Севастополь", "Туринг"),
        ]

        races = []
        for i, (title, location, desc) in enumerate(titles):
            race, _ = Race.objects.get_or_create(
                title=title,
                defaults={
                    "location": location,
                    "description": desc,
                    "date": date.today() + timedelta(days=7 * (i - 2)),
                },
            )
            races.append(race)

        e1, _ = RaceEntry.objects.get_or_create(
            race=races[0],
            user=racer,
            defaults={
                "full_name": "Иванов Алексей Петрович",
                "team_name": "Red Apex",
                "car_description": "Toyota GR86, 2.4 turbo, 320 л.с.",
                "participant_description": "Пилот с опытом кольцевых гонок",
                "experience": "5 лет",
                "racer_class": "Pro",
            },
        )
        e2, _ = RaceEntry.objects.get_or_create(
            race=races[0],
            user=racer2,
            defaults={
                "full_name": "Смирнова Мария Игоревна",
                "team_name": "Nord Wind",
                "car_description": "Honda Civic Type R, 300 л.с.",
                "participant_description": "Специализация — спринт",
                "experience": "3 года",
                "racer_class": "Am",
            },
        )

        RaceResult.objects.get_or_create(
            race=races[0],
            entry=e1,
            defaults={"finish_time": "1:24.310", "place": 1, "notes": "лучший круг"},
        )
        RaceResult.objects.get_or_create(
            race=races[0],
            entry=e2,
            defaults={"finish_time": "1:25.902", "place": 2},
        )

        RaceComment.objects.get_or_create(
            race=races[0],
            author=racer2,
            text="Интересен спонсорский пакет на сезон",
            defaults={
                "race_date": races[0].date,
                "comment_type": RaceComment.TYPE_COOP,
                "rating": 8,
            },
        )

        self.stdout.write(self.style.SUCCESS("OK: demo users admin / racer1 / racer2"))
