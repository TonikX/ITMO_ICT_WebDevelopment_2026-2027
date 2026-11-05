import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warriors_project.settings')
django.setup()

from django.db.models import Count, Min, Max
from warriors_app.models import CarOwner, Car, DriverLicense, Ownership


def run():
    print('1. Дата выдачи самого старшего удостоверения:')
    print(DriverLicense.objects.aggregate(earliest=Min('issue_date')))
    print()

    print('2. Самая поздняя дата владения машиной модели Camry:')
    print(Ownership.objects.filter(car__model='Camry').aggregate(latest=Max('start_date')))
    print()

    print('3. Количество машин для каждого водителя:')
    qs = CarOwner.objects.values('id', 'last_name', 'first_name').annotate(
        cars_count=Count('ownerships__car')
    )
    for row in qs:
        print(row['last_name'], row['first_name'], '-', row['cars_count'])
    print()

    print('4. Количество машин каждой марки:')
    qs = Car.objects.values('brand').annotate(count=Count('id'))
    for row in qs:
        print(row['brand'], '-', row['count'])
    print()

    print('5. Владельцы, отсортированные по дате выдачи удостоверения:')
    qs = (
        CarOwner.objects
        .filter(licenses__isnull=False)
        .order_by('licenses__issue_date')
        .distinct()
    )
    for owner in qs:
        print(owner, '—', owner.licenses.first().issue_date)
    print()


if __name__ == '__main__':
    run()