"""Демо-данные для ЛР2: python manage.py seed_races [--reset].

Создаёт команды, пользователей-гонщиков, гонки (прошедшие и предстоящие),
регистрации, заезды с результатами и комментарии. Даты считаются от сегодняшнего
дня, поэтому прошедшие и предстоящие гонки есть при любом запуске.
"""
import random
from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from races.models import Comment, Heat, Race, Racer, Registration, Result, Team

DEMO_PASSWORD = "Gonka-2026"

TEAMS = [
    ("Северный ветер", "Россия", "Команда из Санкт-Петербурга, кольцевые гонки."),
    ("Volga Motorsport", "Россия", "Заводская команда, туринг."),
    ("Балтик Дрифт", "Латвия", "Дрифт и спринт."),
    ("Ураган", "Казахстан", "Молодая команда, ралли-спринт."),
]

RACERS = [
    # username, ФИО, команда, класс, опыт, описание
    ("racer1", "Смирнов Алексей Игоревич", 0, "pro", 9, "Чемпион города 2025 года, сильная квалификация."),
    ("racer2", "Ковалёва Дарья Сергеевна", 1, "elite", 12, "Опытный пилот туринга, стабильный темп."),
    ("racer3", "Насиров Тимур Ринатович", 3, "amateur", 3, "Бывший картингист, любит мокрую трассу."),
    ("racer4", "Озолс Мартиньш", 2, "pro", 7, "Специалист по коротким трассам."),
    ("racer5", "Гусев Илья Павлович", 0, "rookie", 1, "Первый сезон в кольцевых гонках."),
    ("racer6", "Лебедева Анна Олеговна", 1, "pro", 6, "Инженер команды и пилот."),
    ("racer7", "Ахмадов Руслан Маратович", 3, "amateur", 4, "Ралли-спринт, переходит в кольцо."),
    ("racer8", "Берзиньш Карлис", 2, "elite", 15, "Многократный призёр Балтийской серии."),
    ("racer9", "Фёдоров Максим Андреевич", None, "rookie", 2, "Частный участник без команды."),
    ("racer10", "Ершова Полина Викторовна", 0, "amateur", 5, "Выступает в классе 1600."),
]

CARS = [
    "Lada Vesta Sport TCR", "Hyundai i30 N TCR", "Volkswagen Golf GTI", "BMW M2 CS",
    "Toyota GR86", "Kia Ceed GT", "Subaru BRZ", "Audi RS3 LMS", "Mazda MX-5 Cup", "Lada Granta Cup",
]

# (название, трасса, смещение даты в днях, описание)
RACES = [
    ("Кубок Невы", "Автодром «Северный»", -70, "Открытие сезона, два заезда."),
    ("Осенний гран-при", "Трасса «Волга-Ринг»", -45, "Квалификация, полуфинал и финал."),
    ("Ночная гонка", "Городская трасса «Порт»", -20, "Гонка при искусственном освещении."),
    ("Зимний кубок ИТМО", "Автодром «Северный»", 10, "Студенческий этап на зимней резине."),
    ("Новогодний спринт", "Картодром «Пулково»", 24, "Короткие спринтерские заезды."),
    ("Кубок Ладоги", "Ледовая трасса «Ладога»", 45, "Гонка по льду, шипованная резина."),
]

HEAT_NAMES = ["Квалификация", "Полуфинал", "Финал"]

COMMENTS = [
    ("racing", "Отличная организация, трасса подготовлена хорошо. Будет ли трансляция следующего этапа?"),
    ("cooperation", "Наша компания хотела бы стать партнёром серии. С кем можно связаться?"),
    ("racing", "Какие требования к шинам на следующем этапе?"),
    ("other", "Спасибо волонтёрам и маршалам, всё прошло безопасно."),
    ("racing", "Финальный заезд был очень напряжённым, обгон на последнем круге!"),
]


class Command(BaseCommand):
    help = "Заполняет базу демонстрационными гонками, гонщиками, результатами и комментариями"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="удалить ранее созданные демо-данные")

    @transaction.atomic
    def handle(self, *args, **options):
        rng = random.Random(2026)
        user_model = get_user_model()
        usernames = [r[0] for r in RACERS]

        if options["reset"]:
            Race.objects.filter(title__in=[r[0] for r in RACES]).delete()
            user_model.objects.filter(username__in=usernames).delete()
            Team.objects.filter(name__in=[t[0] for t in TEAMS]).delete()

        if Race.objects.filter(title__in=[r[0] for r in RACES]).exists():
            self.stdout.write(self.style.WARNING("Демо-данные уже есть. Запустите с --reset, чтобы пересоздать."))
            return

        teams = [
            Team.objects.get_or_create(name=name, defaults={"country": country, "description": text})[0]
            for name, country, text in TEAMS
        ]

        racers = []
        for username, full_name, team_index, racer_class, experience, text in RACERS:
            last, first = full_name.split()[:2]
            user, created = user_model.objects.get_or_create(
                username=username, defaults={"first_name": first, "last_name": last}
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
            racer, _ = Racer.objects.get_or_create(
                user=user,
                defaults={
                    "full_name": full_name,
                    "team": teams[team_index] if team_index is not None else None,
                    "racer_class": racer_class,
                    "experience_years": experience,
                    "description": text,
                },
            )
            racers.append(racer)

        today = timezone.localdate()
        tz = timezone.get_current_timezone()
        for title, track, offset, text in RACES:
            race_date = today + timedelta(days=offset)
            race = Race.objects.create(
                title=title, track=track, date=race_date, description=text, registration_open=offset > 0
            )
            past = offset < 0
            count = rng.randint(6, 8) if past else rng.randint(3, 5)
            entrants = rng.sample(racers, count)
            if not past and racers[0] not in entrants and title != "Кубок Ладоги":
                entrants[0] = racers[0]  # у racer1 есть предстоящая регистрация для демонстрации
            registrations = []
            for number, racer in enumerate(entrants, start=1):
                registrations.append(Registration.objects.create(
                    race=race,
                    racer=racer,
                    car_number=number * 7 % 100 or 100,
                    car_description=rng.choice(CARS),
                ))

            heat_names = HEAT_NAMES if title == "Осенний гран-при" else ["Квалификация", "Финал"]
            for index, name in enumerate(heat_names, start=1):
                start = datetime.combine(race_date, time(10 + 2 * index, 0), tzinfo=tz)
                heat = Heat.objects.create(race=race, number=index, name=name, start_time=start, laps=8 + 4 * index)
                if not past:
                    continue
                base = timedelta(minutes=heat.laps * 1, seconds=40 * heat.laps)
                order = registrations[:]
                rng.shuffle(order)
                finish = base
                place = 1
                for reg in order:
                    if rng.random() < 0.08:
                        Result.objects.create(heat=heat, registration=reg, status=Result.Status.DNF)
                        continue
                    finish += timedelta(seconds=rng.uniform(0.3, 6.0))
                    Result.objects.create(heat=heat, registration=reg, position=place, finish_time=finish)
                    place += 1

            if past:
                for comment_type, text_ in rng.sample(COMMENTS, 3):
                    Comment.objects.create(
                        race=race,
                        author=rng.choice(racers).user,
                        heat_date=race_date,
                        text=text_,
                        comment_type=comment_type,
                        rating=rng.randint(6, 10),
                    )

        self.stdout.write(self.style.SUCCESS(
            f"Готово: гонок {Race.objects.count()}, гонщиков {Racer.objects.count()}, "
            f"результатов {Result.objects.count()}, комментариев {Comment.objects.count()}."
        ))
        self.stdout.write(f"Демо-вход: racer1 … racer10, пароль {DEMO_PASSWORD}")
