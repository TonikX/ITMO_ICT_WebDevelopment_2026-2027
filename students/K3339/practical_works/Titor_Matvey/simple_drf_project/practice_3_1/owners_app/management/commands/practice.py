from datetime import date

from django.core.management.base import BaseCommand

from owners_app.models import Car, License, Owner, Possession

class Command(BaseCommand):
    help = 'Практика 3.1: ПЗ1 — данные, ПЗ2 — фильтры и связи, ПЗ3 — агрегации'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('ПЗ1. Создание данных'))

        first_names = ['Олег', 'Анна', 'Игорь', 'Мария', 'Павел', 'Вера', 'Денис']
        last_names = ['Смирнов', 'Кузьмина', 'Рыбаков', 'Орлова', 'Стеблев', 'Яковлева', 'Титов']
        owners = []
        for i, (fn, ln) in enumerate(zip(first_names, last_names), start=1):
            o = Owner.objects.create(
                first_name=fn, last_name=ln,
                birth_date=date(1990 + i % 15, (i * 3) % 12 + 1, (i * 7) % 28 + 1),
                passport=f'7800 {100000 + i * 1111}',
                address=f'СПб, ул. Примерная, {i}',
                nationality='Россия',
            )
            License.objects.create(
                owner=o, number=f'{9000 + i} {i:03d}{i:03d}',
                license_type='B', issued_at=date(2012 + i % 10, i % 12 + 1, 15),
            )
            owners.append(o)

        cars_data = [
            ('Toyota', 'Camry', 'чёрный', 'А001АА78'),
            ('Toyota', 'Corolla', 'белый', 'А002АА78'),
            ('BMW', 'X5', 'чёрный', 'А003АА78'),
            ('Kia', 'Rio', 'серый', 'А004АА78'),
            ('Kia', 'Sportage', 'красный', 'А005АА78'),
            ('Lada', 'Vesta', 'белый', 'А006АА78'),
        ]
        cars = []
        for brand, model, color, number in cars_data:
            c, _ = Car.objects.get_or_create(
                brand=brand, model=model,
                defaults={'color': color, 'state_number': number},
            )
            cars.append(c)

        for i, o in enumerate(owners):
            count = i % 3 + 1
            for j in range(count):
                car = cars[(i + j) % len(cars)]
                Possession.objects.get_or_create(
                    owner=o, car=car,
                    defaults={'started_at': date(2015 + j, (i + j) % 12 + 1, 20)},
                )
        self.stdout.write(f'Владельцев: {Owner.objects.count()}, машин: {Car.objects.count()}, '
                          f'владений: {Possession.objects.count()}')

        self.stdout.write(self.style.MIGRATE_HEADING('ПЗ2. Запросы с фильтрами и связями'))
        toyotas = Car.objects.filter(brand='Toyota')
        self.stdout.write(f'1) Toyota: {list(toyotas.values_list("model", flat=True))}')

        olegs = Owner.objects.filter(first_name='Олег')
        self.stdout.write(f'2) Олеги: {list(olegs.values_list("last_name", flat=True))}')

        some = Owner.objects.first()
        lic = some.license
        self.stdout.write(f'3) Удостоверение владельца id={some.pk}: {lic.number} ({lic.owner})')

        oleg_cars = Owner.objects.filter(cars__color='чёрный').distinct()
        self.stdout.write(f'4) Владельцы чёрных машин: {list(oleg_cars.values_list("last_name", flat=True))}')

        since_2017 = Owner.objects.filter(possessions__started_at__year=2017).distinct()
        self.stdout.write(f'5) Владение с 2017 года: {list(since_2017.values_list("last_name", flat=True))}')

        self.stdout.write(self.style.MIGRATE_HEADING('ПЗ3. Агрегации и группировки'))
        from django.db.models import Count, Max, Min

        earliest = License.objects.aggregate(earliest=Min('issued_at'))
        self.stdout.write(f'1) Самое раннее удостоверение: {earliest["earliest"]}')

        latest_camry = Possession.objects.filter(car__model='Camry').aggregate(latest=Max('started_at'))
        self.stdout.write(f'2) Последнее владение Camry: {latest_camry["latest"]}')

        per_owner = Owner.objects.annotate(total=Count('cars')).values_list('last_name', 'total')
        self.stdout.write(f'3) Машин у владельцев: {list(per_owner)}')

        per_brand = Car.objects.values('brand').annotate(total=Count('id')).order_by('-total')
        self.stdout.write(f'4) Машин по маркам: {list(per_brand)}')

        by_license = Owner.objects.order_by('-license__issued_at').distinct()
        self.stdout.write('5) Владельцы по дате удостоверения: '
                          f'{list(by_license.values_list("last_name", flat=True))}')

        self.stdout.write(self.style.SUCCESS('Практика 3.1 выполнена'))
