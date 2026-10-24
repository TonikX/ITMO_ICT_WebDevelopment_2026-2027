from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from conferences.models import Conference, Review, TalkRegistration, Topic


class Command(BaseCommand):
    help = 'Заполняет конференции, доклады и отзывы'

    def handle(self, *args, **options):
        topics = {}
        for name in (
            'Искусственный интеллект',
            'Базы данных',
            'Веб-технологии',
            'Кибербезопасность',
        ):
            topics[name], _ = Topic.objects.get_or_create(name=name)

        users = {}
        accounts = (
            ('admin', 'admin12345', 'Сергей', 'Волков', True),
            ('anna', 'guest12345', 'Анна', 'Ковалёва', False),
            ('petr', 'guest12345', 'Пётр', 'Орлов', False),
        )
        for username, password, first_name, last_name, staff in accounts:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_staff': staff,
                    'is_superuser': staff,
                },
            )
            if created:
                user.set_password(password)
                user.save()
            users[username] = user

        catalog = (
            (
                'Неделя науки ИТМО',
                date(2026, 4, 14),
                date(2026, 4, 16),
                'Кронверкский проспект, 49',
                'Главный корпус университета, аудитории у внутреннего двора.',
                'Ежегодная встреча студентов и лабораторий.',
                'Тезисы до 4 страниц, очное выступление 10 минут.',
                ['Веб-технологии', 'Базы данных'],
            ),
            (
                'Нейросети и данные',
                date(2026, 5, 20),
                date(2026, 5, 22),
                'Биржевая линия, 14',
                'Корпус на Васильевском острове, зал на втором этаже.',
                'Доклады по моделям, датасетам и качеству данных.',
                'Нужна аннотация и согласие на публикацию тезисов.',
                ['Искусственный интеллект', 'Базы данных'],
            ),
            (
                'Веб и распределённые системы',
                date(2026, 6, 8),
                date(2026, 6, 10),
                'Ломоносова, 9',
                'Учебный корпус с компьютерными классами.',
                'Сервисы, протоколы и архитектура веб-приложений.',
                'Один доклад от автора, регистрация до начала конференции.',
                ['Веб-технологии'],
            ),
            (
                'Информационная безопасность',
                date(2026, 9, 3),
                date(2026, 9, 5),
                'Кронверкский проспект, 49',
                'Актовый зал главного корпуса.',
                'Защита сервисов, модели угроз и практические разборы.',
                'Материалы без эксплуатационных инструкций.',
                ['Кибербезопасность'],
            ),
            (
                'Цифровые гуманитарные науки',
                date(2026, 10, 12),
                date(2026, 10, 13),
                'Кадетская линия, 3',
                'Небольшая аудитория гуманитарного факультета.',
                'Цифровые архивы и методы работы с текстами.',
                'Участие бесплатное для студентов.',
                ['Базы данных'],
            ),
            (
                'Квантовые вычисления',
                date(2026, 11, 18),
                date(2026, 11, 19),
                'Биржевая линия, 16',
                'Лабораторный корпус, лекционный зал.',
                'Алгоритмы и учебные стенды квантовых вычислений.',
                'Доклад на русском или английском, 12 минут.',
                ['Искусственный интеллект'],
            ),
        )
        conferences = {}
        for title, start, end, venue, venue_text, description, terms, topic_names in catalog:
            conference, _ = Conference.objects.get_or_create(
                title=title,
                defaults={
                    'venue_name': venue,
                    'venue_description': venue_text,
                    'start_date': start,
                    'end_date': end,
                    'description': description,
                    'participation_terms': terms,
                },
            )
            conference.topics.set([topics[name] for name in topic_names])
            conferences[title] = conference

        talks = (
            ('anna', 'Неделя науки ИТМО', 'Шаблоны Django в учебном проекте', 'Как устроены списки и формы.', None),
            ('petr', 'Неделя науки ИТМО', 'Нормализация учебной базы', 'Пример схемы конференций.', True),
            ('anna', 'Нейросети и данные', 'Разметка коротких отзывов', 'Оценки от 1 до 10 и текст.', None),
            ('petr', 'Веб и распределённые системы', 'Сессии и права is_staff', 'Чем сотрудник отличается от участника.', False),
            ('anna', 'Информационная безопасность', 'Разделение действий в интерфейсе', 'Кнопки видны только оргкомитету.', None),
            ('petr', 'Цифровые гуманитарные науки', 'Каталог докладов', 'Поиск участников по фамилии.', None),
            ('anna', 'Квантовые вычисления', 'Учебный обзор кубитов', 'Без формул реализации.', None),
            ('petr', 'Квантовые вычисления', 'Симулятор для семинара', 'Как показать алгоритм на паре.', None),
            ('anna', 'Веб и распределённые системы', 'Пагинация длинных списков', 'Номер страницы не сбрасывает фильтр.', None),
        )
        for username, title, talk_title, abstract, recommended in talks:
            TalkRegistration.objects.get_or_create(
                user=users[username],
                conference=conferences[title],
                talk_title=talk_title,
                defaults={'abstract': abstract, 'recommended_for_publication': recommended},
            )

        week = conferences['Неделя науки ИТМО']
        Review.objects.get_or_create(
            conference=week,
            author=users['anna'],
            defaults={
                'conference_start': week.start_date,
                'conference_end': week.end_date,
                'text': 'Удобно смотреть тематики и место проведения на одной странице.',
                'rating': 9,
            },
        )
        self.stdout.write(self.style.SUCCESS('Данные конференций загружены'))
