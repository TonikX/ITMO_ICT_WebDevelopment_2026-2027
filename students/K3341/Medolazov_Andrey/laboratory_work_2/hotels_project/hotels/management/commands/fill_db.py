import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from hotels.models import Amenity, Hotel, Reservation, Review, Room

AMENITIES = ['Wi-Fi', 'Парковка', 'Завтрак', 'Бассейн', 'Спа', 'Фитнес-зал', 'Кондиционер',
             'Мини-бар', 'Телевизор', 'Сейф', 'Вид на море', 'Балкон']

HOTELS = [
    ('Невский берег', 'ООО «Северная столица»', 'Санкт-Петербург', 'Невский пр., 45',
     'Отель в самом центре города, в пяти минутах от Казанского собора и Дворцовой площади.'),
    ('Белые ночи', 'Иванов Петр Сергеевич', 'Санкт-Петербург', 'ул. Рубинштейна, 12',
     'Небольшой бутик-отель в историческом здании XIX века с панорамной террасой.'),
    ('Кронверк', 'ООО «Петроградская гостиница»', 'Санкт-Петербург', 'Кронверкский пр., 49',
     'Уютный отель рядом с Петропавловской крепостью и университетом ИТМО.'),
    ('Арбат Хаус', 'ООО «Арбат Отель Групп»', 'Москва', 'ул. Арбат, 20',
     'Отель на самой известной пешеходной улице Москвы.'),
    ('Москва-Сити Тауэр', 'АО «Сити Хоспиталити»', 'Москва', 'Пресненская наб., 8',
     'Современный отель на высоких этажах башни с видом на деловой центр.'),
    ('Черноморская жемчужина', 'Смирнова Анна Викторовна', 'Сочи', 'Курортный пр., 103',
     'Курортный отель у моря с собственным пляжем и бассейном.'),
    ('Горный воздух', 'ООО «Красная Поляна Резорт»', 'Сочи', 'пос. Эсто-Садок, ул. Горная, 4',
     'Отель у подножия гор, рядом с подъемниками горнолыжного курорта.'),
    ('Казанский кремль', 'ООО «Татарстан Отель»', 'Казань', 'ул. Баумана, 9',
     'Отель в пешей доступности от Кремля и мечети Кул-Шариф.'),
    ('Волжский плес', 'Сидоров Алексей Иванович', 'Казань', 'Кремлевская наб., 33',
     'Тихий отель на набережной Волги с рестораном татарской кухни.'),
]

ROOMS = [
    ('single', 1, 3500),
    ('double', 2, 5200),
    ('double', 2, 6000),
    ('family', 4, 8900),
    ('suite', 2, 14500),
]

GUESTS = [
    ('ivanova', 'Мария', 'Иванова'),
    ('petrov', 'Дмитрий', 'Петров'),
    ('sokolova', 'Елена', 'Соколова'),
    ('kuznetsov', 'Артем', 'Кузнецов'),
    ('volkova', 'Ольга', 'Волкова'),
    ('morozov', 'Игорь', 'Морозов'),
    ('lebedeva', 'Анастасия', 'Лебедева'),
    ('novikov', 'Сергей', 'Новиков'),
]

REVIEWS = [
    (10, 'Все отлично, чистый номер и очень вежливый персонал. Обязательно приеду еще!'),
    (9, 'Хороший номер, удобная кровать, вкусный завтрак. Немного шумно по вечерам.'),
    (8, 'Расположение отличное, номер соответствует описанию. Wi-Fi иногда пропадал.'),
    (7, 'В целом неплохо, но за такую цену ожидал чуть больше.'),
    (6, 'Номер маленький, зато рядом все достопримечательности.'),
    (10, 'Потрясающий вид из окна, отдельное спасибо за ранний заезд.'),
    (5, 'Долго ждали заселения, в номере не работал кондиционер.'),
    (9, 'Тихо, уютно, хорошая звукоизоляция. Рекомендую.'),
]


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными'

    def handle(self, *args, **options):
        random.seed(42)
        Review.objects.all().delete()
        Reservation.objects.all().delete()
        Room.objects.all().delete()
        Hotel.objects.all().delete()
        Amenity.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@hotelbook.ru', 'admin', first_name='Администратор')

        amenities = [Amenity.objects.create(name=name) for name in AMENITIES]

        rooms = []
        for name, owner, city, address, description in HOTELS:
            hotel = Hotel.objects.create(name=name, owner=owner, city=city, address=address, description=description)
            hotel.amenities.set(random.sample(amenities[:6], 3))
            floor = random.randint(1, 3)
            for i, (room_type, capacity, price) in enumerate(ROOMS):
                room = Room.objects.create(
                    hotel=hotel,
                    number=f'{floor}{i + 1:02}',
                    room_type=room_type,
                    capacity=capacity,
                    price=price + random.randint(-5, 10) * 100,
                )
                room.amenities.set(random.sample(amenities[6:], 3))
                rooms.append(room)

        users = []
        for username, first_name, last_name in GUESTS:
            users.append(User.objects.create_user(
                username, f'{username}@mail.ru', 'password123', first_name=first_name, last_name=last_name,
            ))

        today = timezone.localdate()
        now = timezone.now()
        used_rooms = random.sample(rooms, 30)

        for room in used_rooms[:14]:
            start = today - timedelta(days=random.randint(10, 40))
            end = start + timedelta(days=random.randint(2, 7))
            Reservation.objects.create(
                user=random.choice(users), room=room, date_from=start, date_to=end,
                guests=random.randint(1, room.capacity), status='checked_out',
                checked_in_at=now - (today - start), checked_out_at=now - (today - end),
            )

        for room in used_rooms[14:20]:
            start = today - timedelta(days=random.randint(0, 3))
            end = today + timedelta(days=random.randint(1, 5))
            Reservation.objects.create(
                user=random.choice(users), room=room, date_from=start, date_to=end,
                guests=random.randint(1, room.capacity), status='checked_in',
                checked_in_at=now - (today - start),
            )

        for room in used_rooms[20:]:
            start = today + timedelta(days=random.randint(1, 30))
            end = start + timedelta(days=random.randint(1, 6))
            Reservation.objects.create(
                user=random.choice(users), room=room, date_from=start, date_to=end,
                guests=random.randint(1, room.capacity), status='booked',
            )

        for reservation in Reservation.objects.filter(status='checked_out'):
            rating, text = random.choice(REVIEWS)
            Review.objects.create(
                room=reservation.room, user=reservation.user, rating=rating, text=text,
                date_from=reservation.date_from, date_to=reservation.date_to,
            )

        self.stdout.write(self.style.SUCCESS(
            f'Отелей: {Hotel.objects.count()}, номеров: {Room.objects.count()}, '
            f'бронирований: {Reservation.objects.count()}, отзывов: {Review.objects.count()}'
        ))
