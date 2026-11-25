from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from practice.models import Profession, Skill, SkillOfWarrior, Warrior
from zoo import models


class Command(BaseCommand):
    help = "Заполнить пустую базу демонстрационными данными"

    @transaction.atomic
    def handle(self, *args, **options):
        if models.Zoo.objects.exists() or Warrior.objects.exists():
            raise CommandError("Команда предназначена для пустой базы")
        local = models.Zoo.objects.create(name="Северный зоопарк", address="Санкт-Петербург", is_local=True)
        guest = models.Zoo.objects.create(name="Зоопарк партнёр", address="Петрозаводск")
        zone = models.HabitatZone.objects.create(
            name="Северные леса", continent="Евразия", country="Россия", description="Леса и водоёмы",
        )
        bird = models.Species.objects.create(
            common_name="Кряква", scientific_name="Anas platyrhynchos",
            animal_class="bird", report_group="Птицы",
        )
        reptile = models.Species.objects.create(
            common_name="Обыкновенный уж", scientific_name="Natrix natrix",
            animal_class="reptile", report_group="Рептилии", normal_temperature_c="26.0",
        )
        birds = models.Department.objects.create(name="Птицы")
        reptiles = models.Department.objects.create(name="Рептилии")
        building = models.Building.objects.create(department=birds, name="Птичник", season="winter")
        aviary = models.Enclosure.objects.create(
            department=birds, building=building, number="П-01", capacity=4, has_pool=True,
        )
        models.Enclosure.objects.create(department=birds, building=building, number="П-02", capacity=2)
        terrarium = models.Enclosure.objects.create(department=reptiles, number="Р-01", capacity=1)
        animals = []
        for number, name, species, zoo, enclosure in [
            ("001", "Ива", bird, local, aviary), ("002", "Камыш", bird, guest, aviary),
            ("003", "Лист", reptile, local, terrarium), ("004", "Плющ", reptile, local, None),
        ]:
            animals.append(models.Animal.objects.create(
                inventory_number=number, name=name, birth_date=date(2022, 5, 12), sex="female",
                species=species, habitat_zone=zone, owner_zoo=zoo, enclosure=enclosure,
            ))
        for year in (2024, 2025):
            models.BirdWintering.objects.create(
                animal=animals[0], wintering_code="TR-01", wintering_country="Турция",
                departure_date=date(year, 11, 1), arrival_date=date(year + 1, 3, 18),
            )
            models.ReptileHibernation.objects.create(
                animal=animals[2], starts_on=date(year, 10, 20), ends_on=date(year + 1, 3, 5),
            )
        keeper = models.Employee.objects.create(
            personnel_number="С-01", last_name="Ветрова", first_name="Анна", role="keeper",
            birth_date=date(1997, 4, 8), phone="+70000000001",
        )
        vet = models.Employee.objects.create(
            personnel_number="В-01", last_name="Орлов", first_name="Илья", role="vet",
            birth_date=date(1995, 9, 15), phone="+70000000002",
        )
        grain = models.Diet.objects.create(number="К-01", name="Зерновая смесь", diet_type="standard", contents="Зерно и зелень")
        insects = models.Diet.objects.create(number="К-02", name="Рацион для ужей", diet_type="standard", contents="Корм по графику")
        now = timezone.now()
        for animal in animals:
            animal.employees.add(keeper, vet)
            models.DietAssignment.objects.create(
                animal=animal, diet=grain if animal.species_id == bird.id else insects,
                started_at=now - timedelta(days=30),
            )
        today = timezone.localdate()
        for animal, lessor, lessee, cost in [
            (animals[1], guest, local, "18000.00"), (animals[3], local, guest, "24000.00"),
        ]:
            models.Lease.objects.create(
                animal=animal, lessor=lessor, lessee=lessee, starts_on=today - timedelta(days=7),
                ends_on=today + timedelta(days=30), total_cost=cost, transferred_at=now - timedelta(days=7),
            )
        profession = Profession.objects.create(title="Разработчик", description="Пишет приложения")
        skill = Skill.objects.create(title="Работа с API")
        warrior = Warrior.objects.create(name="Ярослав", race="d", level=4, profession=profession)
        SkillOfWarrior.objects.create(warrior=warrior, skill=skill, level=3)
        self.stdout.write(self.style.SUCCESS("Демонстрационные данные готовы"))
