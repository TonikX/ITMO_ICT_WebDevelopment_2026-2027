"""Idempotent fictional demonstration data. Never resets existing passwords."""
from datetime import timedelta, datetime, time
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from racing.models import Race, Driver, Entry, Heat, Comment


class Command(BaseCommand):
    help = 'Создать учебные гонки, 12 гонщиков и локальные демонстрационные аккаунты.'

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        schedule = [
            ('neva-sprint', 'Нева. Финальный спринт', 'Игора Драйв', 'Ленинградская область', -16, 'finished', 'race-orange.webp', '5.183', 14),
            ('moscow-autumn', 'Московский осенний кубок', 'Moscow Raceway', 'Московская область', 7, 'open', 'race-yellow.webp', '3.931', 15),
            ('sochi-endurance', 'Южная дистанция', 'Сочи Автодром', 'Сириус', 14, 'open', 'race-orange.webp', '5.848', 18),
            ('kazan-time-attack', 'Казань. Time Attack', 'KazanRing', 'Казань', 21, 'open', 'race-blue.webp', '3.476', 12),
            ('smolensk-sprint', 'Смоленское кольцо', 'Смоленское кольцо', 'Смоленская область', 28, 'open', 'race-yellow.webp', '3.357', 13),
            ('nring-cup', 'Нижегородский кубок', 'Нижегородское кольцо', 'Нижний Новгород', 35, 'open', 'race-blue.webp', '3.222', 9),
            ('neva-winter', 'Северный вызов', 'Игора Драйв', 'Ленинградская область', 42, 'scheduled', 'race-orange.webp', '5.183', 14),
            ('moscow-sprint', 'Столичный спринт', 'Moscow Raceway', 'Московская область', -28, 'finished', 'race-yellow.webp', '3.931', 15),
        ]
        races = []
        for i, (slug, title, track, location, offset, status, image, length, corners) in enumerate(schedule, 1):
            start = today + timedelta(days=offset)
            race, _ = Race.objects.get_or_create(slug=slug, defaults={
                'title': title, 'track': track, 'location': location, 'start_date': start,
                'end_date': start + timedelta(days=1), 'round_number': i, 'status': status,
                'image': image, 'length_km': length, 'corners': corners, 'capacity': 30,
                'description': 'Кольцевая гонка в классах PRO, PRO–AM и AM. Два зачётных заезда, '
                'отдельный хронометраж каждой попытки. Стартовый номер выбирается при подаче заявки. '
                'Судейская коллегия публикует время и результаты в официальном протоколе.',
            })
            races.append(race)
        names = [
            ('Волков Артём Сергеевич', 'Northline Racing', 'Porsche 911 GT3 R · 4.2 л · 565 л.с.', 'PRO', 9),
            ('Морозова Анна Дмитриевна', 'Aero Motorsport', 'Mercedes-AMG GT3 · 6.2 л · 550 л.с.', 'PRO', 7),
            ('Соколов Максим Андреевич', 'Vector Racing', 'BMW M4 GT3 · 3.0 л · 590 л.с.', 'PRO-AM', 5),
            ('Лебедев Илья Романович', 'Northline Racing', 'Audi R8 LMS GT3 · 5.2 л · 585 л.с.', 'PRO', 8),
            ('Крылова Елена Игоревна', 'Aero Motorsport', 'Ferrari 296 GT3 · 3.0 л · 600 л.с.', 'PRO-AM', 4),
            ('Орлов Дмитрий Алексеевич', 'Track Unit', 'Porsche 718 Cayman GT4 · 4.0 л · 500 л.с.', 'AM', 3),
            ('Зайцев Никита Павлович', 'Vector Racing', 'BMW M4 GT4 · 3.0 л · 550 л.с.', 'PRO-AM', 6),
            ('Белова Мария Олеговна', 'Track Unit', 'Toyota GR Supra GT4 · 3.0 л · 450 л.с.', 'AM', 2),
            ('Кузнецов Роман Викторович', 'West Corner', 'McLaren 720S GT3 · 4.0 л · 500 л.с.', 'PRO', 11),
            ('Фёдоров Алексей Ильич', 'West Corner', 'Aston Martin Vantage GT3 · 4.0 л · 535 л.с.', 'PRO-AM', 5),
            ('Новикова Дарья Михайловна', 'Track Unit', 'Alpine A110 GT4 · 1.8 л · 350 л.с.', 'AM', 2),
            ('Егоров Павел Денисович', 'Vector Racing', 'Lamborghini Huracán GT3 · 5.2 л · 580 л.с.', 'PRO-AM', 4),
        ]
        drivers = []
        for i, (name, team, car, category, experience) in enumerate(names):
            username = 'racer' if i == 0 else f'driver{i + 1:02d}'
            user, created = User.objects.get_or_create(username=username, defaults={'first_name': name})
            if created:
                user.set_password('DemoRace2026!')
                user.save()
            driver, _ = Driver.objects.get_or_create(user=user, defaults={
                'full_name': name, 'team': team, 'car': car, 'racing_class': category, 'experience': experience,
                'bio': 'Участник кольцевых гонок. Специализация — короткие спринты и точная работа '
                'на торможении. Выступает в командном и личном зачёте.',
            })
            drivers.append(driver)
        for race_index, race in enumerate(races):
            for i, driver in enumerate(drivers[:12 if race.status == 'finished' else 4 + race_index % 4]):
                entry, _ = Entry.objects.get_or_create(race=race, driver=driver, defaults={'number': [27, 11, 63, 7, 88, 14, 23, 44, 9, 55, 31, 96][i]})
                if race.status == 'finished':
                    for attempt in [1, 2]:
                        Heat.objects.get_or_create(entry=entry, attempt=attempt, defaults={
                            'started_at': timezone.make_aware(datetime.combine(race.start_date, time(12 + attempt, i))),
                            'duration': timedelta(seconds=102.385 + i * .827 + (attempt - 1) * .214),
                            'position': i + 1, 'status': 'finished',
                        })
        admin, created = User.objects.get_or_create(username='judge', defaults={'first_name': 'Судья чемпионата', 'is_staff': True, 'is_superuser': True})
        if created:
            admin.set_password('DemoControl2026!')
            admin.save()
        race = races[0]
        for driver, kind, rating, text in [
            (drivers[0], 'racing', 9, 'Хороший темп во втором заезде. Подскажите, где будут опубликованы условия следующего этапа?'),
            (drivers[1], 'cooperation', 10, 'Ищем партнёров для совместной подготовки к следующему этапу. Готовы обсудить тренировки и обмен телеметрией.'),
            (drivers[2], 'other', 8, 'Удобно смотреть время каждой попытки отдельно. Спасибо судейской команде за подробный протокол.'),
        ]:
            Comment.objects.get_or_create(race=race, author=driver.user, text=text, defaults={
                'date_from': race.start_date, 'date_to': race.end_date, 'kind': kind, 'rating': rating,
            })
        self.stdout.write(self.style.SUCCESS('Демонстрационные данные готовы. Все гонки, участники и результаты вымышлены.'))
        self.stdout.write('Локальные аккаунты: racer / DemoRace2026!; judge / DemoControl2026!')
