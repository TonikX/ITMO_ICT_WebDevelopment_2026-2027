from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from project_first_app.models import Owner, Car, Ownership


class Command(BaseCommand):
    help = 'Добавить начальные вымышленные данные практической работы'

    def handle(self, *args, **options):
        owners = []
        for username, first_name, last_name in [('owner1', 'Иван', 'Иванов'), ('owner2', 'Пётр', 'Петров')]:
            owner, created = Owner.objects.get_or_create(username=username, defaults={'first_name': first_name, 'last_name': last_name})
            if created:
                owner.set_unusable_password()
                owner.save()
            owners.append(owner)

        for number in range(1, 5):
            car, _ = Car.objects.get_or_create(registration_number=f'TEST{number}', defaults={'brand': 'Учебная', 'model': f'Модель {number}'})
            for owner, start, end in [(owners[0], 2018, 2020), (owners[1], 2021, 2023)]:
                if number <= 3:
                    Ownership.objects.get_or_create(owner=owner, car=car, defaults={
                        'start_date': datetime(start, 1, 1, tzinfo=timezone.utc),
                        'end_date': datetime(end, 1, 1, tzinfo=timezone.utc),
                    })
        self.stdout.write('Начальные учебные данные добавлены')
