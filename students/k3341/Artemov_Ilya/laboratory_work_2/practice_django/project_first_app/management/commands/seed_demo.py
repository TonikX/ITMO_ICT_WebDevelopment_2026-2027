from datetime import date
from django.core.management.base import BaseCommand
from project_first_app.models import Car, CarOwner, DriverLicense, Ownership


class Command(BaseCommand):
    help = "Добавить учебные данные практик: 6 владельцев, 7 автомобилей, историю владения."

    def handle(self, *args, **options):
        people = [("Иван", "Иванов"), ("Пётр", "Петров"), ("Анна", "Смирнова"),
                  ("Ольга", "Соколова"), ("Сергей", "Попов"), ("Мария", "Козлова")]
        owners = []
        for index, (first, last) in enumerate(people, 1):
            owner, created = CarOwner.objects.get_or_create(username=f"owner{index}", defaults={
                "first_name": first, "last_name": last, "birth_date": date(1990 + index, 3, 10),
                "passport_number": f"4000{index:06}", "home_address": f"Санкт-Петербург, Учебная ул., д. {index}",
                "nationality": "Русский" if index in (1, 2, 5) else "Русская",
            })
            if created:
                owner.set_unusable_password()
                owner.save(update_fields=["password"])
            owners.append(owner)
        cars = []
        for index, (brand, model, color) in enumerate([
            ("Toyota", "Corolla", "Белый"), ("Kia", "Rio", "Серый"), ("Lada", "Vesta", "Синий"),
            ("Skoda", "Octavia", "Чёрный"), ("Hyundai", "Solaris", "Красный"),
            ("Renault", "Logan", "Белый"), ("Volkswagen", "Polo", "Серебристый"),
        ], 1):
            car, _ = Car.objects.get_or_create(registration_number=f"А{index:03}АА178", defaults={
                "brand": brand, "model_name": model, "color": color,
            })
            cars.append(car)
        history = [(0, 0, date(2018, 1, 1), date(2019, 12, 31)),
                   (0, 1, date(2020, 1, 1), date(2021, 12, 31)),
                   (0, 2, date(2022, 1, 1), date(2023, 12, 31)),
                   (1, 0, date(2020, 1, 1), None),
                   (1, 1, date(2022, 1, 1), None),
                   (1, 3, date(2024, 1, 1), None)]
        for owner_index, car_index, start, end in history:
            if not Ownership.objects.filter(owner=owners[owner_index], car=cars[car_index], start_date=start).exists():
                ownership = Ownership(owner=owners[owner_index], car=cars[car_index], start_date=start, end_date=end)
                ownership.full_clean()
                ownership.save()
        for index, owner in enumerate(owners[:2], 1):
            DriverLicense.objects.get_or_create(number=f"7800{index:06}", defaults={
                "owner": owner, "category": "B", "issue_date": date(2015, 6, index),
            })
        self.stdout.write(self.style.SUCCESS("Учебные данные практик добавлены. Существующие записи сохранены."))
