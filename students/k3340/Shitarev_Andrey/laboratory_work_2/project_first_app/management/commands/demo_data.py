from datetime import date, timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from project_first_app.models import Driver, Race, Registration, Run, Comment

class Command(BaseCommand):
    help = 'Добавить вымышленные данные гонок'

    def handle(self, *args, **kwargs):
        races = []
        for name, day, place in [('Кубок города', date(2026, 6, 1), 'Санкт-Петербург'), ('Летняя гонка', date(2026, 7, 1), 'Москва')]:
            race, _ = Race.objects.get_or_create(name=name, defaults={'date': day, 'place': place})
            races.append(race)
        for number in range(1, 4):
            user, created = User.objects.get_or_create(username=f'driver{number}')
            if created:
                user.set_unusable_password()
                user.save()
            driver, _ = Driver.objects.get_or_create(user=user, defaults={'full_name': f'Гонщик {number}', 'team': f'Команда {number}', 'car_description': 'Гоночный автомобиль', 'description': 'Участник гонок', 'experience': '2 года', 'driver_class': 'Любитель'})
            registration, _ = Registration.objects.get_or_create(driver=driver, race=races[0])
            Run.objects.get_or_create(registration=registration, date=races[0].date, defaults={'duration': timedelta(minutes=number + 1), 'place': number})
            if number <= 2:
                Comment.objects.get_or_create(author=user, race=races[0], defaults={'run_date': races[0].date, 'text': 'Интересная гонка', 'comment_type': 'other', 'rating': 8})
        Registration.objects.get_or_create(driver=driver, race=races[1])
        self.stdout.write('Демонстрационные данные добавлены')
