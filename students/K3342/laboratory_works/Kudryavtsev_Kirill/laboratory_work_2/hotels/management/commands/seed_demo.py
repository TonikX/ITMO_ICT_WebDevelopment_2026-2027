import getpass
import os
from datetime import timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from hotels.models import Booking, Hotel, Review, Room


class Command(BaseCommand):
    help = 'Добавить демонстрационные отели и номера. --with-users добавляет учебные аккаунты и проживания.'

    def add_arguments(self, parser):
        parser.add_argument('--with-users', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        items = [
            ('Северный двор', 'Санкт-Петербург', 'Литейный проспект, 18', 'ООО Север', 'Небольшой отель в центре города. Тихий двор и круглосуточная стойка регистрации.'),
            ('Лесная пристань', 'Выборг', 'Парковая улица, 7', 'ИП Соколов', 'Отель рядом с парком. Подходит для семейных поездок и прогулок.'),
            ('Берег', 'Сортавала', 'Набережная, 12', 'ООО Берег', 'Просторные номера у воды. Завтрак и место для отдыха на первом этаже.'),
        ]
        rooms = []
        for name, city, address, owner, description in items:
            hotel, _ = Hotel.objects.get_or_create(name=name, defaults=dict(city=city, address=address, owner=owner, description=description))
            for number, kind, price, capacity in [('101', 'single', 2800, 1), ('102', 'double', 4200, 2), ('201', 'family', 5800, 4), ('202', 'suite', 7500, 3)]:
                room, _ = Room.objects.get_or_create(hotel=hotel, number=number, defaults=dict(room_type=kind, price=price, capacity=capacity, amenities='Wi-Fi, душ, рабочий стол' + (', кухня' if kind == 'family' else '')))
                rooms.append(room)
        if options['with_users']:
            users = []
            for name, staff, first in [('manager', True, 'Администратор'), ('guest', False, 'Алексей')]:
                user, created = User.objects.get_or_create(username=name, defaults=dict(first_name=first, last_name='' if staff else 'Иванов', email=f'{name}@example.test', is_staff=staff, is_superuser=staff))
                if created or not user.has_usable_password():
                    password = os.getenv('DEMO_ADMIN_PASSWORD' if staff else 'DEMO_GUEST_PASSWORD') or getpass.getpass(f'Пароль для {name}: ')
                    if len(password) < 8:
                        raise ValueError('Пароль должен содержать не менее 8 символов.')
                    user.set_password(password)
                    user.save()
                users.append(user)
            now = timezone.now()
            today = timezone.localdate()
            Booking.objects.get_or_create(room=rooms[0], user=users[1], arrival=today, departure=today+timedelta(days=2), defaults={'guests': 1})
            past, _ = Booking.objects.get_or_create(room=rooms[1], user=users[1], arrival=today-timedelta(days=8), departure=today-timedelta(days=5), defaults=dict(guests=2, status=Booking.OUT, checked_in_at=now-timedelta(days=8), checked_out_at=now-timedelta(days=5)))
            Review.objects.get_or_create(booking=past, defaults=dict(room=past.room, user=past.user, arrival=timezone.localtime(past.checked_in_at).date(), departure=timezone.localtime(past.checked_out_at).date(), text='Тихий номер, удобное расположение. Заселились вовремя.', rating=9))
        self.stdout.write(self.style.SUCCESS('Готово: 3 отеля, 12 номеров.'))
