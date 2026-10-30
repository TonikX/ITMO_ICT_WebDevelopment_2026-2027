from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from hotel_app.models import Employee, Floor, Guest, Room, RoomType


class Command(BaseCommand):
    help = "Добавить демонстрационные справочники без заселений и расписания."

    @transaction.atomic
    def handle(self, *args, **options):
        for capacity, name, price in [(1, "Одноместный", 3000), (2, "Двухместный", 5000),
                                      (3, "Трёхместный", 7000)]:
            room_type, _ = RoomType.objects.get_or_create(
                capacity=capacity, defaults={"name": name, "price_per_night": price}
            )
            floor, _ = Floor.objects.get_or_create(number=capacity)
            Room.objects.get_or_create(
                number=f"DEMO-{capacity}",
                defaults={"floor": floor, "room_type": room_type, "phone": f"10{capacity}"},
            )
        for index in [1, 2]:
            Guest.objects.get_or_create(
                passport_series="DEMO", passport_number=f"FAKE-{index}",
                defaults={"first_name": f"Тест{index}", "last_name": "ДемоГость",
                          "arrival_city": "Тестовый город"},
            )
            Employee.objects.get_or_create(
                first_name=f"Тест{index}", last_name="ДемоСотрудник", hired_on=date(2026, 1, 1)
            )
        self.stdout.write(self.style.SUCCESS("Демонстрационные справочники готовы."))
