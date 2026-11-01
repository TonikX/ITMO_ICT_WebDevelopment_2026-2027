import os
import secrets
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from conferences.models import Conference, Participation, Review, Topic, User

TOPICS = ["Искусственный интеллект", "Веб-технологии", "Базы данных", "Кибербезопасность", "Робототехника"]

# (название, город, площадка, номера тематик, начало через N дней от сегодняшнего дня)
CONFERENCES = [
    ("Международная конференция по ИИ", "Санкт-Петербург", "Университет ИТМО", [0, 3], -60),
    ("Веб-технологии и сервисы", "Москва", "Технопарк на Ленинских горах", [1, 2], -30),
    ("Современные СУБД", "Казань", "Университет Иннополис", [2], 14),
    ("Безопасность информационных систем", "Новосибирск", "Академгородок", [3, 1], 40),
    ("Робототехника и автоматизация", "Санкт-Петербург", "Политех", [4, 0], 70),
    ("Данные и ML в промышленности", "Екатеринбург", "УрФУ", [0, 2], 100),
    ("Frontend-инженерия", "Москва", "Digital October", [1], 130),
]

TALKS = [
    "Нейросети в диагностике",
    "Масштабирование Django-приложений",
    "Индексы PostgreSQL на практике",
    "Анализ уязвимостей веб-приложений",
]

PEOPLE = [
    ("ivanov", "Иван", "Иванов", "ИТМО", "к.т.н."),
    ("petrova", "Мария", "Петрова", "МГУ", "д.ф.-м.н."),
    ("sidorov", "Пётр", "Сидоров", "СПбПУ", "аспирант"),
    ("kuznetsova", "Анна", "Кузнецова", "Иннополис", "к.ф.-м.н."),
]

DECISIONS = [Participation.Result.RECOMMENDED, Participation.Result.NOT_RECOMMENDED]


def password_from_env(name):
    """Пароль из переменной окружения или случайный: в коде паролей нет."""
    return os.environ.get(name) or secrets.token_urlsafe(12)


class Command(BaseCommand):
    help = "Заполняет БД демонстрационными данными (повторный запуск ничего не дублирует)."

    def handle(self, *args, **options):
        created_users = []

        def add_user(username, password, **fields):
            user, created = User.objects.get_or_create(username=username, defaults=fields)
            if created:
                user.set_password(password)
                user.save()
                created_users.append(f"{username} / {password}")
            return user

        if not User.objects.filter(username="admin").exists():
            admin_password = password_from_env("SEED_ADMIN_PASSWORD")
            User.objects.create_superuser(
                "admin", "admin@example.com", admin_password, first_name="Админ", last_name="Системный"
            )
            created_users.append(f"admin / {admin_password}")

        user_password = password_from_env("SEED_USER_PASSWORD")
        users = [
            add_user(username, user_password, first_name=first, last_name=last, organization=org, academic_degree=degree)
            for username, first, last, org, degree in PEOPLE
        ]

        topics = [Topic.objects.get_or_create(name=name)[0] for name in TOPICS]
        today = date.today()
        conferences = []
        for title, city, venue, topic_numbers, offset in CONFERENCES:
            start = today + timedelta(days=offset)
            conference, created = Conference.objects.get_or_create(
                title=title,
                defaults=dict(
                    city=city,
                    venue_name=venue,
                    start_date=start,
                    end_date=start + timedelta(days=2),
                    description=f"Ежегодная конференция «{title}»: доклады, секции и круглые столы.",
                    venue_description=f"{venue}: удобная транспортная доступность, кофе-брейки.",
                    participation_terms="Заявка с тезисами до начала конференции; лучшие доклады публикуются в сборнике.",
                ),
            )
            if created:
                conference.topics.set(topics[number] for number in topic_numbers)
            conferences.append(conference)

        # Доклады подают на первые четыре конференции. Для прошедших уже есть решения и отзывы.
        for ci, conference in enumerate(conferences[:4]):
            past = conference.end_date < today
            for ui, user in enumerate(users):
                _, created = Participation.objects.get_or_create(
                    conference=conference,
                    user=user,
                    defaults=dict(
                        talk_title=TALKS[(ci + ui) % len(TALKS)],
                        abstract="Краткие тезисы доклада.",
                        result=DECISIONS[(ci + ui) % 2] if past else Participation.Result.PENDING,
                    ),
                )
                if created and past:
                    Review.objects.create(
                        conference=conference,
                        author=user,
                        start_date=conference.start_date,
                        end_date=conference.end_date,
                        rating=6 + (ci + ui) % 5,
                        text="Хорошая организация, интересные доклады.",
                    )

        self.stdout.write(self.style.SUCCESS("Готово."))
        for line in created_users:
            self.stdout.write(f"Создан пользователь (логин / пароль): {line}")
