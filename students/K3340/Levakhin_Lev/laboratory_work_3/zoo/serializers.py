from django.core.exceptions import ValidationError as ModelValidationError
from rest_framework import serializers

from . import models


class CheckedSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        model = self.Meta.model
        instance = model()
        if self.instance:
            for field in model._meta.concrete_fields:
                setattr(instance, field.attname, getattr(self.instance, field.attname))
            instance._state.adding = False
        for field, value in attrs.items():
            setattr(instance, field, value)
        try:
            instance.full_clean()
        except ModelValidationError as error:
            raise serializers.ValidationError(error.message_dict) from error
        self.check_rules(instance)
        return attrs

    def check_rules(self, instance):
        pass


class SpeciesSerializer(CheckedSerializer):
    class Meta:
        model = models.Species
        fields = "__all__"

    def check_rules(self, species):
        if self.instance and self.instance.animal_class != species.animal_class and species.animals.exists():
            raise serializers.ValidationError({"animal_class": "Вид уже назначен животным"})


class ZooSerializer(CheckedSerializer):
    class Meta:
        model = models.Zoo
        fields = "__all__"

    def check_rules(self, zoo):
        if self.instance and self.instance.is_local != zoo.is_local and (
            zoo.owned_animals.exists() or zoo.leases_as_lessee.exists() or zoo.leases_as_lessor.exists()
        ):
            raise serializers.ValidationError({"is_local": "Зоопарк уже используется в учёте"})


class BuildingSerializer(CheckedSerializer):
    class Meta:
        model = models.Building
        fields = "__all__"

    def check_rules(self, building):
        if self.instance and building.enclosures.exclude(department=building.department).exists():
            raise serializers.ValidationError({"department": "В здании уже есть вольеры другого отдела"})


class EnclosureSerializer(CheckedSerializer):
    class Meta:
        model = models.Enclosure
        fields = "__all__"

    def check_rules(self, enclosure):
        if enclosure.building:
            building = models.Building.objects.select_for_update().get(pk=enclosure.building_id)
            if building.department_id != enclosure.department_id:
                raise serializers.ValidationError({"building": "Здание должно находиться в том же отделе"})
        if self.instance:
            residents = enclosure.animals.count()
            if residents > enclosure.capacity:
                raise serializers.ValidationError({"capacity": "В вольере уже больше животных"})
            if residents and enclosure.department_id != self.instance.department_id:
                raise serializers.ValidationError({"department": "Сначала освободите вольер"})


class DepartmentSerializer(CheckedSerializer):
    enclosures = EnclosureSerializer(many=True, read_only=True)

    class Meta:
        model = models.Department
        fields = ["id", "name", "enclosures"]


class EmployeeSerializer(CheckedSerializer):
    class Meta:
        model = models.Employee
        fields = "__all__"


class AnimalSerializer(CheckedSerializer):
    employees = EmployeeSerializer(many=True, read_only=True)
    species_name = serializers.CharField(source="species.common_name", read_only=True)
    enclosure_number = serializers.CharField(source="enclosure.number", read_only=True, default=None)

    class Meta:
        model = models.Animal
        fields = "__all__"

    def check_rules(self, animal):
        animal.species = models.Species.objects.select_for_update().get(pk=animal.species_id)
        animal.owner_zoo = models.Zoo.objects.select_for_update().get(pk=animal.owner_zoo_id)
        if animal.purchase_received_on and not animal.owner_zoo.is_local:
            raise serializers.ValidationError({"owner_zoo": "Покупку оформляет наш зоопарк"})
        if self.instance:
            if animal.owner_zoo_id != self.instance.owner_zoo_id and animal.leases.exists():
                raise serializers.ValidationError({"owner_zoo": "Для животного уже есть договоры"})
            if animal.species.animal_class != models.Species.AnimalClass.BIRD and animal.winterings.exists():
                raise serializers.ValidationError({"species": "У животного есть записи о зимовке"})
            if animal.species.animal_class != models.Species.AnimalClass.REPTILE and animal.hibernations.exists():
                raise serializers.ValidationError({"species": "У животного есть записи о спячке"})
        if not self.instance or animal.enclosure_id != self.instance.enclosure_id:
            current = self.instance.enclosure if self.instance else None
            if current and not animal.enclosure:
                raise serializers.ValidationError({"enclosure": "Освобождение вольера оформляется при передаче"})
            if animal.enclosure:
                enclosure = models.Enclosure.objects.select_for_update().get(pk=animal.enclosure_id)
                if current and current.department_id != enclosure.department_id:
                    raise serializers.ValidationError({"enclosure": "Пересадка разрешена в пределах отдела"})
                if enclosure.animals.exclude(pk=animal.pk).count() >= enclosure.capacity:
                    raise serializers.ValidationError({"enclosure": "Вольер заполнен"})
                if not current and (not animal.owner_zoo.is_local or (
                    self.instance and animal.leases.filter(
                        transferred_at__isnull=False, returned_at__isnull=True
                    ).exists()
                )):
                    raise serializers.ValidationError({"enclosure": "Заселение оформляется при приёме животного"})


class PeriodSerializer(CheckedSerializer):
    def check_rules(self, period):
        animal = models.Animal.objects.select_for_update().get(pk=period.animal_id)
        if self.animal_class and animal.species.animal_class != self.animal_class:
            raise serializers.ValidationError({"animal": "Период не подходит для класса животного"})
        start = getattr(period, self.start_field)
        end = getattr(period, self.end_field)
        end_filter = models.Q(**{f"{self.end_field}__isnull": True}) | models.Q(
            **{f"{self.end_field}__{self.end_lookup}": start}
        )
        existing = self.Meta.model.objects.filter(animal=animal).exclude(pk=period.pk).filter(end_filter)
        if end is not None:
            existing = existing.filter(**{f"{self.start_field}__{self.start_lookup}": end})
        if existing.exists():
            raise serializers.ValidationError({"animal": "Периоды для одного животного пересекаются"})


class BirdWinteringSerializer(PeriodSerializer):
    animal_class = models.Species.AnimalClass.BIRD
    start_field, end_field = "departure_date", "arrival_date"
    start_lookup, end_lookup = "lte", "gte"

    class Meta:
        model = models.BirdWintering
        fields = "__all__"


class ReptileHibernationSerializer(PeriodSerializer):
    animal_class = models.Species.AnimalClass.REPTILE
    start_field, end_field = "starts_on", "ends_on"
    start_lookup, end_lookup = "lte", "gte"

    class Meta:
        model = models.ReptileHibernation
        fields = "__all__"


class DietAssignmentSerializer(PeriodSerializer):
    animal_class = None
    start_field, end_field = "started_at", "ended_at"
    start_lookup, end_lookup = "lt", "gt"

    class Meta:
        model = models.DietAssignment
        fields = "__all__"


class LeaseSerializer(CheckedSerializer):
    class Meta:
        model = models.Lease
        fields = "__all__"
        read_only_fields = ["transferred_at", "returned_at"]

    def check_rules(self, lease):
        if self.instance and self.instance.transferred_at:
            raise serializers.ValidationError("Договор уже исполнялся")
        if lease.lessor.is_local == lease.lessee.is_local:
            raise serializers.ValidationError({"lessee": "Одна из сторон должна быть нашим зоопарком"})
        animal = models.Animal.objects.select_for_update().get(pk=lease.animal_id)
        if animal.owner_zoo_id != lease.lessor_id:
            raise serializers.ValidationError({"lessor": "Арендодатель должен быть владельцем животного"})
