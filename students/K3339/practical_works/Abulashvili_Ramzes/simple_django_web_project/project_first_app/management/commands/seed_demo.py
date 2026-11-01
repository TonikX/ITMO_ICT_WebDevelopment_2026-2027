from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from project_first_app.models import Car, CarOwner, DrivingLicense, Ownership


class Command(BaseCommand):
    help = "Добавляет учебных автовладельцев, автомобили и историю владения."

    @transaction.atomic
    def handle(self, *args, **options):
        owners = []
        for username, first_name, last_name, birth in [
            ("ivan_petrov", "Иван", "Петров", date(1995, 3, 12)),
            ("anna_smirnova", "Анна", "Смирнова", date(1998, 6, 8)),
            ("pavel_orlov", "Павел", "Орлов", date(1993, 9, 20)),
            ("elena_sokolova", "Елена", "Соколова", date(1999, 2, 10)),
            ("mikhail_volkov", "Михаил", "Волков", date(1999, 2, 10)),
            ("olga_morozova", "Ольга", "Морозова", date(1999, 2, 10)),
        ]:
            owner, created = CarOwner.objects.get_or_create(username=username, defaults={
                "first_name": first_name, "last_name": last_name, "birth_date": birth,
                "passport_number": f"0000 {len(owners) + 1:06d}", "home_address": "Учебный адрес, Санкт-Петербург", "nationality": "Русский",
            })
            if created:
                owner.set_unusable_password()
                owner.save()
            owners.append(owner)
            DrivingLicense.objects.get_or_create(owner=owner, number=f"00000000{len(owners):02d}", defaults={"category": "B", "issue_date": date(2015, 5, 10)})
        cars = []
        for plate, brand, model, color in [
            ("А111АА178", "Lada", "Vesta", "Белый"),
            ("В222ВВ178", "Toyota", "Corolla", "Серый"),
            ("Е333ЕЕ178", "Kia", "Rio", "Красный"),
            ("К444КК178", "Skoda", "Octavia", "Синий"),
            ("Т100ТТ178", "Lada", "Granta 1", "Белый"),
            ("Т200ТТ178", "Lada", "Granta 2", "Белый"),
            ("Т300ТТ178", "Lada", "Granta 3", "Белый"),
        ]:
            car, created = Car.objects.get_or_create(plate_number=plate, defaults={"brand": brand, "model_name": model, "color": color})
            cars.append(car)
        for car in cars[:3]:
            Ownership.objects.get_or_create(car=car, owner=owners[0], start_date=date(2020, 1, 1), defaults={"end_date": date(2021, 12, 31)})
        for car in (cars[0], cars[1], cars[3]):
            Ownership.objects.get_or_create(car=car, owner=owners[1], start_date=date(2022, 1, 1))
        self.stdout.write(self.style.SUCCESS("Учебные данные готовы: 6 владельцев, 7 автомобилей и 6 записей владения."))
