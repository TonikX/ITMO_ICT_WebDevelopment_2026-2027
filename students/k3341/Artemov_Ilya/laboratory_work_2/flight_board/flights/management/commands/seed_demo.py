from datetime import datetime, time, timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from flights.models import Flight, Reservation, Review


class Command(BaseCommand):
    help = "Добавить 12 учебных рейсов, пассажиров и пример отзыва."

    def handle(self, *args, **options):
        users = []
        for index, (first, last) in enumerate([("Анна", "Смирнова"), ("Павел", "Иванов")], 1):
            user, created = get_user_model().objects.get_or_create(username=f"passenger{index}", defaults={
                "first_name": first, "last_name": last,
            })
            if created:
                user.set_unusable_password()
                user.save(update_fields=["password"])
            users.append(user)
        day = timezone.localdate() + timedelta(days=1)
        routes = [("Москва, SVO", "Аэрофлот", "SU"), ("Казань, KZN", "Россия", "FV"),
                  ("Сочи, AER", "Победа", "DP"), ("Калининград, KGD", "Аэрофлот", "SU"),
                  ("Екатеринбург, SVX", "Уральские авиалинии", "U6"), ("Новосибирск, OVB", "S7 Airlines", "S7")]
        flights = []
        for index in range(12):
            city, airline, prefix = routes[index % len(routes)]
            departure = timezone.make_aware(datetime.combine(day + timedelta(days=index // 6), time(7 + index % 6 * 2)))
            is_departure = index % 2 == 0
            flight, _ = Flight.objects.get_or_create(number=f"{prefix}{100 + index}", defaults={
                "airline": airline, "origin": "Санкт-Петербург, LED" if is_departure else city,
                "destination": city if is_departure else "Санкт-Петербург, LED",
                "departure_at": departure, "arrival_at": departure + timedelta(hours=2),
                "direction": "departure" if is_departure else "arrival", "gate": f"A{index + 1}", "seat_count": 30,
            })
            flights.append(flight)
        for index, user in enumerate(users, 1):
            Reservation.objects.get_or_create(flight=flights[0], seat_number=index, defaults={
                "user": user, "passenger_name": user.get_full_name(),
                "checked_in": index == 1, "ticket_number": "DEMO-000001" if index == 1 else None,
            })
        Review.objects.get_or_create(flight=flights[0], user=users[0], defaults={
            "flight_date": timezone.localdate(flights[0].departure_at), "rating": 9,
            "text": "Учебный пример отзыва: понятное расписание и удобное бронирование.",
        })
        self.stdout.write(self.style.SUCCESS("Учебные рейсы и пассажиры добавлены. Существующие записи сохранены."))
