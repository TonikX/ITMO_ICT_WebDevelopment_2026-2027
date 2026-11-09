from datetime import date, datetime, time, timedelta
from pathlib import Path
from secrets import token_urlsafe
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from flights.models import Booking, Flight, Review, User
from project_first_app.models import Car, DriverLicense, Ownership


class Command(BaseCommand):
    help = 'Создать демонстрационные рейсы, пассажиров и данные практик.'

    def handle(self, *args, **options):
        access = []
        people = [('admin', 'Анна', 'Морозова', True), ('traveler', 'Александр', 'Соколов', False),
                  ('marina', 'Марина', 'Волкова', False), ('ivan', 'Иван', 'Орлов', False),
                  ('elena', 'Елена', 'Белова', False), ('pavel', 'Павел', 'Лебедев', False)]
        for index, (username, first, last, staff) in enumerate(people):
            user, created = User.objects.get_or_create(username=username, defaults={
                'first_name': first, 'last_name': last, 'email': f'{username}@example.com',
                'is_staff': staff, 'is_superuser': staff, 'birth_date': date(1990 + index, 3, 12),
                'passport_number': f'DEMO-{index + 1:04}', 'home_address': 'Учебный адрес', 'nationality': 'Учебные данные'})
            if created:
                password = token_urlsafe(12)
                user.set_password(password)
                user.save()
                access.append(f'{username}: {password}')
        if access:
            path = settings.BASE_DIR / '.runtime' / 'access.txt'
            path.parent.mkdir(exist_ok=True)
            with path.open('a') as stream:
                stream.write('\n'.join(access) + '\n')
            path.chmod(0o600)
            self.stdout.write('Локальные демонстрационные доступы: .runtime/access.txt')
        routes = [
            ('Санкт-Петербург', 'LED', 'Москва', 'SVO', 95),
            ('Москва', 'SVO', 'Сочи', 'AER', 220),
            ('Санкт-Петербург', 'LED', 'Стамбул', 'IST', 260),
            ('Казань', 'KZN', 'Санкт-Петербург', 'LED', 140),
            ('Санкт-Петербург', 'LED', 'Калининград', 'KGD', 120),
            ('Москва', 'SVO', 'Екатеринбург', 'SVX', 150),
            ('Санкт-Петербург', 'LED', 'Мурманск', 'MMK', 115),
            ('Сочи', 'AER', 'Санкт-Петербург', 'LED', 240),
        ]
        start = timezone.localdate() + timedelta(days=1)
        for index in range(18):
            origin, origin_code, destination, destination_code, minutes = routes[index % len(routes)]
            departure = timezone.make_aware(datetime.combine(start + timedelta(days=index // 8), time(7 + index % 8 * 2, 15 if index % 2 else 30)))
            flight, _ = Flight.objects.get_or_create(number=f'NL {101 + index}', departure_at=departure, defaults={
                'airline': 'Nordline' if index % 3 else 'Nordline Regional', 'origin': origin, 'origin_code': origin_code,
                'destination': destination, 'destination_code': destination_code, 'arrival_at': departure + timedelta(minutes=minutes),
                'kind': 'arrival' if index % 4 == 3 else 'departure', 'gate': f'{"AB"[index % 2]}{index % 12 + 1:02}',
                'status': 'delayed' if index == 2 else 'scheduled', 'aircraft': 'Airbus A320' if index % 2 else 'Airbus A321',
                'price': 6400 + index * 1100, 'capacity': 180})
            if index < 3:
                for seat_index, username in enumerate(['traveler', 'marina', 'ivan']):
                    passenger = User.objects.get(username=username)
                    Booking.objects.get_or_create(flight=flight, user=passenger, defaults={
                        'passenger_name': passenger.get_full_name(), 'seat': f'{seat_index + 1}A',
                        'ticket_number': f'NL-{index + 1:03}-{seat_index + 1:04}', 'checked_in': True})
                Review.objects.get_or_create(flight=flight, user=User.objects.get(username='marina'), defaults={
                    'flight_date': timezone.localtime(departure).date(), 'rating': 9,
                    'text': 'Удобное бронирование и внимательный экипаж. Хорошее начало путешествия.'})
        car_data = [('Toyota', 'Camry', 'Синий'), ('Kia', 'Rio', 'Белый'), ('Lada', 'Vesta', 'Чёрный'),
                    ('Hyundai', 'Solaris', 'Серый'), ('Skoda', 'Octavia', 'Белый'), ('Renault', 'Logan', 'Синий'),
                    ('Volkswagen', 'Polo', 'Красный')]
        for index, (brand, model, color) in enumerate(car_data):
            car, _ = Car.objects.get_or_create(registration_number=f'A{index + 100}AA178', defaults={'brand': brand, 'model': model, 'color': color})
            for username, begin, end in [('traveler', date(2020, 1, 1), date(2021, 12, 31)), ('marina', date(2022, 1, 1), None)]:
                Ownership.objects.get_or_create(car=car, owner=User.objects.get(username=username), defaults={'start_date': begin, 'end_date': end})
        for username in ['traveler', 'marina', 'ivan', 'elena', 'pavel']:
            DriverLicense.objects.get_or_create(owner=User.objects.get(username=username), number=f'DEMO{User.objects.get(username=username).pk:06}',
                                                defaults={'category': 'B', 'issued_at': date(2018, 5, 1)})
        self.stdout.write(self.style.SUCCESS(f'Готово: {Flight.objects.count()} рейсов, {Booking.objects.count()} бронирований, {Car.objects.count()} автомобилей.'))
