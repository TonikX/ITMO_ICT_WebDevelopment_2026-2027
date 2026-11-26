"""
Практика 3.1, задание 3 — агрегация и аннотация.

    python manage.py practice31_task3
"""
from django.core.management.base import BaseCommand
from django.db.models import Count, Max, Min

from project_first_app.models import Car, CarOwner, DriverLicense, Ownership


class Command(BaseCommand):
    help = 'Практика 3.1, задание 3: aggregate / annotate / values / order_by'

    def show(self, title, code, result):
        self.stdout.write(self.style.MIGRATE_HEADING(f'\n{title}'))
        self.stdout.write(f'>>> {code}')
        self.stdout.write(str(result))

    def handle(self, *args, **options):
        # 1. Дата выдачи самого старшего удостоверения
        self.show('1. Дата выдачи самого старшего водительского удостоверения',
                  "DriverLicense.objects.aggregate(oldest=Min('issue_date'))",
                  DriverLicense.objects.aggregate(oldest=Min('issue_date')))

        # 2. Самая поздняя дата владения машиной заданной модели
        model_name = 'Camry'
        self.show(f'2. Самая поздняя дата начала владения машиной модели {model_name}',
                  f"Ownership.objects.filter(car__model='{model_name}').aggregate(latest=Max('start_date'))",
                  Ownership.objects.filter(car__model=model_name).aggregate(latest=Max('start_date')))

        # 3. Количество машин для каждого водителя
        owners = CarOwner.objects.filter(is_superuser=False).annotate(cars_count=Count('cars'))
        self.show('3. Количество машин для каждого водителя',
                  "CarOwner.objects.annotate(cars_count=Count('cars'))",
                  '\n'.join(f'{o}: {o.cars_count}' for o in owners))

        # 4. Количество машин каждой марки (GROUP BY через values)
        self.show('4. Количество машин каждой марки',
                  "Car.objects.values('brand').annotate(count=Count('id')).order_by('brand')",
                  Car.objects.values('brand').annotate(count=Count('id')).order_by('brand'))

        # 5. Владельцы, отсортированные по дате выдачи удостоверения
        sorted_owners = (CarOwner.objects.filter(licenses__isnull=False)
                         .order_by('licenses__issue_date').distinct())
        self.show('5. Автовладельцы, отсортированные по дате выдачи удостоверения',
                  "CarOwner.objects.filter(licenses__isnull=False)"
                  ".order_by('licenses__issue_date').distinct()",
                  '\n'.join(f'{o}: {o.licenses.first().issue_date}' for o in sorted_owners))
