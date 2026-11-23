from datetime import date, datetime, time, timedelta
import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from flights.models import Airline, Booking, Flight, Review
from project_first_app.models import Car, DriverLicense, Ownership


class Command(BaseCommand):
    help = 'Создать демонстрационные данные без удаления существующих записей.'

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        demo_password = os.environ.get('SKYBOARD_DEMO_PASSWORD', 'SkyboardDemo2026!')
        for username, staff, first, last in [('admin', True, 'Дмитрий', 'Афанасьев'),
                                              ('passenger', False, 'Анна', 'Соколова')]:
            user, created = User.objects.get_or_create(username=username, defaults={
                'first_name': first, 'last_name': last, 'is_staff': staff, 'is_superuser': staff})
            if created:
                user.set_password(demo_password)
                user.save()
        admin = User.objects.get(username='admin')
        passenger = User.objects.get(username='passenger')
        airlines = [Airline.objects.get_or_create(code=code, defaults={'name': name})[0]
                    for code, name in [('SU', 'Аэрофлот'), ('S7', 'S7 Airlines'), ('FV', 'Россия')]]
        cities = ['Москва', 'Казань', 'Сочи', 'Екатеринбург', 'Калининград', 'Мурманск',
                  'Новосибирск', 'Самара', 'Уфа', 'Минеральные Воды', 'Омск', 'Пермь']
        days = ['2026-10-02', '2026-12-18', '2026-02-11', '2026-05-27',
                '2026-09-07', '2026-11-30', '2027-01-14', '2027-03-09',
                '2027-05-22', '2027-07-16', '2027-09-28', '2027-12-12']
        flights = []
        for i, city in enumerate(cities):
            number = f'{airlines[i % 3].code}{1400 + i}'
            flight = Flight.objects.filter(number=number).first()
            if not flight:
                departure = timezone.make_aware(datetime.combine(date.fromisoformat(days[i]), time((20, 23, 2, 5)[i % 4])))
                flight = Flight.objects.create(number=number, airline=airlines[i % 3],
                    origin='Санкт-Петербург' if i % 2 == 0 else city,
                    destination=city if i % 2 == 0 else 'Санкт-Петербург',
                    departure_at=departure, arrival_at=departure + timedelta(hours=2 + i % 3),
                    direction='departure' if i % 2 == 0 else 'arrival', gate=f'{10 + i}A', capacity=24,
                    status='scheduled' if departure > timezone.now() else 'completed')
            flights.append(flight)
        if not Booking.objects.filter(flight=flights[5], user=passenger).exists() and flights[5].is_bookable:
            Booking.objects.create(flight=flights[5], user=passenger, passenger_name=str(passenger), seat=3)
        if not Booking.objects.filter(flight=flights[1], user=admin).exists() and flights[1].is_bookable:
            Booking.objects.create(flight=flights[1], user=admin, passenger_name=str(admin), seat=8,
                                   ticket_number='DEMO-1008', checked_in=True)
        if not Review.objects.filter(flight=flights[5], user=passenger).exists():
            Review.objects.create(flight=flights[5], user=passenger, rating=9,
                                  text='Демонстрационный отзыв: удобная посадка и внимательный экипаж.')
        owners = []
        for i, (first, last) in enumerate([('Иван', 'Петров'), ('Мария', 'Иванова'), ('Алексей', 'Орлов'),
                                          ('Елена', 'Смирнова'), ('Олег', 'Кузнецов'), ('Ирина', 'Попова'),
                                          ('Антон', 'Лебедев'), ('Дарья', 'Волкова')]):
            owner, created = User.objects.get_or_create(username=f'owner{i+1}', defaults={
                'first_name': first, 'last_name': last, 'birth_date': date(1990+i, 3, 6),
                'passport_number': f'DEMO-{i+1:04}', 'home_address': 'Учебный адрес, Санкт-Петербург',
                'nationality': 'Учебные данные'})
            if created:
                owner.set_password(demo_password)
                owner.save()
            owners.append(owner)
            DriverLicense.objects.get_or_create(number=f'D{i+1:09}', defaults={
                'owner': owner, 'category': 'B', 'issued_at': date(2018, 1, 1)})
        for i, (brand, model) in enumerate([('Toyota', 'Camry'), ('Kia', 'Rio'), ('Skoda', 'Octavia'),
                                           ('Lada', 'Vesta'), ('Hyundai', 'Solaris'), ('Renault', 'Logan'),
                                           ('Volkswagen', 'Polo')]):
            car = Car.objects.get_or_create(plate_number=f'DEMO-{i+1}', defaults={
                'brand': brand, 'model_name': model, 'color': ['Белый', 'Синий', 'Серый'][i % 3]})[0]
            if i < 3:
                for owner, start, end in [(owners[0], date(2020, 1, 1), date(2022, 1, 1)),
                                           (owners[1], date(2022, 1, 1), None)]:
                    Ownership.objects.get_or_create(car=car, owner=owner, start_date=start, defaults={'end_date': end})
            else:
                Ownership.objects.get_or_create(car=car, owner=owners[i], start_date=date(2023, 1, 1))
        self.stdout.write(self.style.SUCCESS('Демо готово: 12 рейсов, пользователи, бронирования, отзыв, 8 автовладельцев и 7 автомобилей.'))
        self.stdout.write('Новые демо-аккаунты: admin / passenger. Пароль задан через SKYBOARD_DEMO_PASSWORD или локальный демо-пароль.')
