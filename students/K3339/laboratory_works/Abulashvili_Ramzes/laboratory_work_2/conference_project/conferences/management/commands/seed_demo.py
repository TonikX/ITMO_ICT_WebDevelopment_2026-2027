from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from conferences.models import Conference, Registration, Review, Topic, Venue


class Command(BaseCommand):
    help = "Добавляет учебные конференции и примеры выступлений."

    @transaction.atomic
    def handle(self, *args, **options):
        topics = [Topic.objects.get_or_create(name=name)[0] for name in ["Веб-разработка", "Анализ данных", "Информационная безопасность"]]
        venues = []
        for name, city, address, description in [
            ("Университетский конференц-центр", "Санкт-Петербург", "Учебная улица, 10", "Аудитории для докладов, проекторы и зона для обсуждений."),
            ("Научный центр", "Москва", "Научная улица, 15", "Конференц-зал и отдельные помещения для тематических секций."),
        ]:
            venue, created = Venue.objects.get_or_create(name=name, defaults={"city": city, "address": address, "description": description})
            venues.append(venue)
        conferences = []
        titles = ["Современные веб-технологии", "Данные и научные исследования", "Безопасность цифровых систем", "Веб-сервисы и приложения", "Методы анализа данных", "Открытые технологии в науке"]
        for index, title in enumerate(titles):
            start = date(2026, 11, 16) + timedelta(days=index * 7)
            conference, created = Conference.objects.get_or_create(title=title, defaults={
                "venue": venues[index % 2], "start_date": start, "end_date": start + timedelta(days=1),
                "description": f"Научная конференция «{title}» посвящена исследованиям и практическим результатам в области информационных технологий. Участники представляют доклады и обсуждают опыт разработки.",
                "participation_terms": "Для участия с докладом зарегистрируйтесь на сайте, укажите тему выступления, организацию и краткую аннотацию. Участие бесплатное. По итогам выступления организатор принимает решение о рекомендации к публикации.",
            })
            if created:
                conference.topics.add(topics[index % len(topics)])
            conferences.append(conference)
        users = []
        for username, first_name, last_name in [("demo_anna", "Анна", "Смирнова"), ("demo_pavel", "Павел", "Орлов")]:
            user, created = get_user_model().objects.get_or_create(username=username, defaults={"first_name": first_name, "last_name": last_name})
            if created:
                user.set_unusable_password()
                user.save()
            users.append(user)
        for conference, author, title, result in [
            (conferences[0], users[0], "Шаблонизация веб-приложений", Registration.Result.RECOMMENDED),
            (conferences[0], users[1], "Организация серверной части сайта", Registration.Result.PENDING),
            (conferences[1], users[0], "Подготовка данных для исследования", Registration.Result.NOT_RECOMMENDED),
        ]:
            Registration.objects.get_or_create(conference=conference, author=author, defaults={"presentation_title": title, "affiliation": "Учебный исследовательский центр", "abstract": "Практические результаты и примеры применения выбранного подхода.", "result": result})
        self.stdout.write(self.style.SUCCESS("Добавлены 6 конференций, 3 тематики, 2 площадки и 3 заявки."))
