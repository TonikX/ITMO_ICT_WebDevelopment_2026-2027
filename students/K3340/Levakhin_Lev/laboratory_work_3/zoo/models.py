from django.db import models
from django.db.models import F, Q

PROTECT = models.PROTECT


class Zoo(models.Model):
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=255)
    is_local = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["is_local"], condition=Q(is_local=True), name="one_local_zoo"),
        ]


class HabitatZone(models.Model):
    name = models.CharField(max_length=120)
    continent = models.CharField(max_length=80)
    country = models.CharField(max_length=80)
    description = models.TextField()


# Общие данные об одном виде, например у нас по заданию Кряква это и Ива и Камыш
class Species(models.Model):
    class AnimalClass(models.TextChoices):
        MAMMAL = "mammal", "Млекопитающие"
        BIRD = "bird", "Птицы"
        REPTILE = "reptile", "Рептилии"
        AMPHIBIAN = "amphibian", "Земноводные"
        FISH = "fish", "Рыбы"
        OTHER = "other", "Прочие"

    scientific_name = models.CharField(max_length=120, unique=True)
    common_name = models.CharField(max_length=120)
    animal_class = models.CharField(max_length=12, choices=AnimalClass)
    report_group = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    normal_temperature_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(animal_class="reptile", normal_temperature_c__isnull=False)
                | (~Q(animal_class="reptile") & Q(normal_temperature_c__isnull=True)),
                name="species_reptile_temperature",
            ),
        ]


# Отдел зоопарка, например отдел птиц
class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)


# Здание внутри отдела
class Building(models.Model):
    class Season(models.TextChoices):
        SUMMER = "summer", "Летний"
        WINTER = "winter", "Зимний"

    department = models.ForeignKey(Department, PROTECT, related_name="buildings")
    name = models.CharField(max_length=120)
    season = models.CharField(max_length=6, choices=Season)


# Вольер
class Enclosure(models.Model):
    department = models.ForeignKey(Department, PROTECT, related_name="enclosures")
    building = models.ForeignKey(Building, PROTECT, related_name="enclosures", null=True, blank=True)
    number = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()
    is_isolated = models.BooleanField(default=False)
    has_pool = models.BooleanField(default=False)
    has_indoor_area = models.BooleanField(default=False)
    equipment = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["department", "number"], name="enclosure_department_number"),
            models.CheckConstraint(condition=Q(capacity__gt=0), name="enclosure_positive_capacity"),
        ]


class Employee(models.Model):
    class Role(models.TextChoices):
        KEEPER = "keeper", "Смотритель"
        VET = "vet", "Ветеринар"

    personnel_number = models.CharField(max_length=20, unique=True)
    last_name = models.CharField(max_length=80)
    first_name = models.CharField(max_length=80)
    patronymic = models.CharField(max_length=80, blank=True)
    birth_date = models.DateField()
    phone = models.CharField(max_length=24)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=6, choices=Role)


# Карточка животного
class Animal(models.Model):
    class Sex(models.TextChoices):
        FEMALE = "female", "Самка"
        MALE = "male", "Самец"

    inventory_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=80)
    birth_date = models.DateField()
    sex = models.CharField(max_length=6, choices=Sex)
    species = models.ForeignKey(Species, PROTECT, related_name="animals")
    care_notes = models.TextField(blank=True)
    habitat_zone = models.ForeignKey(HabitatZone, PROTECT, related_name="animals")
    owner_zoo = models.ForeignKey(Zoo, PROTECT, related_name="owned_animals")
    enclosure = models.ForeignKey(Enclosure, PROTECT, related_name="animals", null=True, blank=True)
    purchase_seller_name = models.CharField(max_length=120, blank=True)
    purchase_received_on = models.DateField(null=True, blank=True)
    employees = models.ManyToManyField(Employee, through="CareAssignment", related_name="animals")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(purchase_seller_name="", purchase_received_on__isnull=True)
                | (~Q(purchase_seller_name="") & Q(purchase_received_on__isnull=False)),
                name="animal_purchase_pair",
            ),
        ]


class BirdWintering(models.Model):
    animal = models.ForeignKey(Animal, PROTECT, related_name="winterings")
    wintering_code = models.CharField(max_length=30)
    wintering_country = models.CharField(max_length=80)
    departure_date = models.DateField()
    arrival_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-departure_date", "id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(arrival_date__isnull=True) | Q(arrival_date__gte=F("departure_date")),
                name="wintering_date_order",
            ),
        ]


class ReptileHibernation(models.Model):
    animal = models.ForeignKey(Animal, PROTECT, related_name="hibernations")
    starts_on = models.DateField()
    ends_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-starts_on", "id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(ends_on__isnull=True) | Q(ends_on__gte=F("starts_on")),
                name="hibernation_date_order",
            ),
        ]


class Diet(models.Model):
    class Type(models.TextChoices):
        STANDARD = "standard", "Обычный"
        JUNIOR = "junior", "Детский"
        DIET = "diet", "Диетический"
        ENRICHED = "enriched", "Усиленный"

    number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    diet_type = models.CharField(max_length=10, choices=Type)
    contents = models.TextField()


# Какой рацион назначили конкретному животному и на какой период
class DietAssignment(models.Model):
    animal = models.ForeignKey(Animal, PROTECT, related_name="diet_assignments")
    diet = models.ForeignKey(Diet, PROTECT, related_name="assignments")
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(ended_at__isnull=True) | Q(ended_at__gt=F("started_at")),
                name="diet_assignment_date_order",
            ),
            models.UniqueConstraint(fields=["animal"], condition=Q(ended_at__isnull=True), name="one_open_diet"),
        ]


# Одно закрепление сотрудника за животным, тут реализовал мени ту мени
class CareAssignment(models.Model):
    animal = models.ForeignKey(Animal, models.CASCADE, related_name="care_assignments")
    employee = models.ForeignKey(Employee, models.CASCADE, related_name="care_assignments")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["animal", "employee"], name="unique_care_assignment"),
        ]


class Lease(models.Model):
    animal = models.ForeignKey(Animal, PROTECT, related_name="leases")
    lessor = models.ForeignKey(Zoo, PROTECT, related_name="leases_as_lessor")
    lessee = models.ForeignKey(Zoo, PROTECT, related_name="leases_as_lessee")
    starts_on = models.DateField()
    ends_on = models.DateField()
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    transferred_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=~Q(lessor=F("lessee")), name="lease_different_zoos"),
            models.CheckConstraint(condition=Q(ends_on__gte=F("starts_on")), name="lease_date_order"),
            models.CheckConstraint(condition=Q(total_cost__gte=0), name="lease_nonnegative_cost"),
            models.CheckConstraint(
                condition=Q(returned_at__isnull=True)
                | Q(transferred_at__isnull=False, returned_at__gte=F("transferred_at")),
                name="lease_transfer_order",
            ),
            models.UniqueConstraint(
                fields=["animal"], condition=Q(transferred_at__isnull=False, returned_at__isnull=True),
                name="one_active_lease",
            ),
        ]
