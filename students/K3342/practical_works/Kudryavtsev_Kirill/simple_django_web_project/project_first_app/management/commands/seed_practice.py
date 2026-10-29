from datetime import date
from django.core.management.base import BaseCommand
from project_first_app.models import Car, CarOwner, DriverLicense, Ownership


class Command(BaseCommand):
    help = 'Добавить учебные данные автовладельцев (все сведения вымышленные).'

    def handle(self, *args, **kwargs):
        owners = []
        for i, (first, last) in enumerate([('Анна', 'Орлова'), ('Иван', 'Смирнов'), ('Мария', 'Лебедева')], 1):
            owner, created = CarOwner.objects.get_or_create(username=f'owner{i}', defaults=dict(first_name=first, last_name=last, birth_date=date(1990+i, 3, 10), passport_number=f'ТЕСТ-{i:04}', home_address=f'Учебный город, улица Примерная, {i}', nationality='Учебное значение'))
            if created:
                owner.set_unusable_password()
                owner.save()
            owners.append(owner)
            DriverLicense.objects.get_or_create(owner=owner, number=f'TEST{i:06}', defaults=dict(category='B', issue_date=date(2018, 1, 1)))
        cars = []
        for i, (brand, model, color) in enumerate([('Lada', 'Vesta', 'Белый'), ('Skoda', 'Octavia', 'Серый'), ('Kia', 'Rio', 'Синий'), ('Toyota', 'Corolla', 'Чёрный')], 1):
            car, _ = Car.objects.get_or_create(plate=f'ТЕСТ-{i:03}', defaults=dict(brand=brand, model=model, color=color))
            cars.append(car)
        for owner, start, end in [(owners[0], date(2019, 1, 1), date(2020, 1, 1)), (owners[1], date(2020, 1, 1), date(2021, 1, 1))]:
            for car in cars[:3]:
                item, created = Ownership.objects.get_or_create(owner=owner, car=car, start_date=start, defaults={'end_date': end})
                item.full_clean()
        Ownership.objects.get_or_create(owner=owners[2], car=cars[3], start_date=date(2021, 1, 1))
        self.stdout.write('Добавлены 3 владельца, 4 автомобиля, удостоверения и непересекающиеся периоды владения.')
