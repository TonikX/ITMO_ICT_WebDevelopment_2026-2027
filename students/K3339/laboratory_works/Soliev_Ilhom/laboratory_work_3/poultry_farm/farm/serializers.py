from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from rest_framework import serializers

from .models import (
    Breed,
    BreedSeasonDiet,
    Cage,
    Chicken,
    ChickenCageAssignment,
    ChickenWeightRecord,
    Diet,
    EggProductionRecord,
    Employee,
    EmployeeCageAssignment,
    EmploymentContract,
    FarmUser,
    Workshop,
)
from .services import (
    validate_cage_chicken_capacity,
    validate_chicken_cage_assignment,
    validate_employee_cage_assignment,
    validate_employee_assignment_removal,
    validate_workshop_cage_capacity,
)


def _raise_api_validation_error(error):
    detail = getattr(error, "message_dict", None) or getattr(error, "messages", str(error))
    raise serializers.ValidationError(detail)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmUser
        fields = ("id", "username", "email", "role", "created_at")
        read_only_fields = fields


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Public self-registration always creates a worker account."""

    class Meta(DjoserUserCreateSerializer.Meta):
        model = FarmUser
        fields = ("id", "username", "email", "password")


class EmploymentContractSerializer(serializers.ModelSerializer):
    salary = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)

    class Meta:
        model = EmploymentContract
        fields = (
            "id",
            "employee",
            "contract_number",
            "signed_at",
            "started_at",
            "ended_at",
            "salary",
            "dismissal_reason",
        )

    def validate(self, attrs):
        started_at = attrs.get("started_at", getattr(self.instance, "started_at", None))
        ended_at = attrs.get("ended_at", getattr(self.instance, "ended_at", None))
        if started_at and ended_at and ended_at < started_at:
            raise serializers.ValidationError({"ended_at": "Дата увольнения не может быть раньше даты начала работы."})
        return attrs


class CageSummarySerializer(serializers.ModelSerializer):
    workshop_number = serializers.IntegerField(source="workshop.workshop_number", read_only=True)

    class Meta:
        model = Cage
        fields = ("id", "workshop", "workshop_number", "row_number", "cage_number", "capacity_chickens")
        read_only_fields = fields


class ChickenAssignmentReadSerializer(serializers.ModelSerializer):
    cage = CageSummarySerializer(read_only=True)

    class Meta:
        model = ChickenCageAssignment
        fields = ("id", "cage", "valid_from", "valid_to")


class EmployeeAssignmentReadSerializer(serializers.ModelSerializer):
    cage = CageSummarySerializer(read_only=True)

    class Meta:
        model = EmployeeCageAssignment
        fields = ("id", "cage", "assigned_from", "assigned_to")


class WorkshopSerializer(serializers.ModelSerializer):
    capacity_cages = serializers.IntegerField(min_value=1)
    cages = CageSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Workshop
        fields = ("id", "workshop_number", "name", "capacity_cages", "cages")

    def validate(self, attrs):
        capacity = attrs.get("capacity_cages", getattr(self.instance, "capacity_cages", None))
        if self.instance and capacity is not None and self.instance.cages.count() > capacity:
            raise serializers.ValidationError(
                {"capacity_cages": "Вместимость не может быть меньше числа клеток в цехе."}
            )
        return attrs


class CageSerializer(serializers.ModelSerializer):
    capacity_chickens = serializers.IntegerField(min_value=1)
    workshop_number = serializers.IntegerField(source="workshop.workshop_number", read_only=True)
    current_chickens = serializers.SerializerMethodField()

    class Meta:
        model = Cage
        fields = (
            "id",
            "workshop",
            "workshop_number",
            "row_number",
            "cage_number",
            "capacity_chickens",
            "current_chickens",
        )
        read_only_fields = ("current_chickens",)

    def validate(self, attrs):
        capacity = attrs.get("capacity_chickens", getattr(self.instance, "capacity_chickens", None))
        if self.instance and capacity is not None:
            try:
                validate_cage_chicken_capacity(self.instance, capacity=capacity)
            except DjangoValidationError as exc:
                _raise_api_validation_error(exc)
        workshop = attrs.get("workshop", getattr(self.instance, "workshop", None))
        if workshop:
            changing_workshop = self.instance and workshop.pk != self.instance.workshop_id
            if not self.instance or changing_workshop:
                try:
                    validate_workshop_cage_capacity(
                        workshop,
                        exclude_cage_id=self.instance.pk if self.instance else None,
                    )
                except DjangoValidationError as exc:
                    _raise_api_validation_error(exc)
        return attrs

    def get_current_chickens(self, obj):
        today = timezone.localdate()
        return list(
            obj.chicken_assignments.filter(valid_from__lte=today)
            .filter(Q(valid_to__isnull=True) | Q(valid_to__gte=today))
            .filter(chicken__arrived_at__lte=today)
            .filter(Q(chicken__removed_at__isnull=True) | Q(chicken__removed_at__gte=today))
            .values_list("chicken_id", flat=True)
            .distinct()
        )


class BreedSerializer(serializers.ModelSerializer):
    average_eggs_per_month = serializers.IntegerField(min_value=0)
    average_weight_grams = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=0)

    class Meta:
        model = Breed
        fields = ("id", "name", "average_eggs_per_month", "average_weight_grams")


class DietSerializer(serializers.ModelSerializer):
    daily_cost_per_chicken = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)

    class Meta:
        model = Diet
        fields = ("id", "diet_number", "content", "daily_cost_per_chicken")


class BreedSeasonDietSerializer(serializers.ModelSerializer):
    breed_name = serializers.CharField(source="breed.name", read_only=True)
    diet_number = serializers.CharField(source="diet.diet_number", read_only=True)

    class Meta:
        model = BreedSeasonDiet
        fields = ("id", "breed", "breed_name", "diet", "diet_number", "season")


class EmployeeReadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    contracts = EmploymentContractSerializer(many=True, read_only=True)
    cage_assignments = EmployeeAssignmentReadSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = ("id", "user", "full_name", "passport_issued_by", "passport_issued_at", "contracts", "cage_assignments")


class EmployeeWriteSerializer(serializers.ModelSerializer):
    passport_series = serializers.CharField(max_length=10, write_only=True)
    passport_number = serializers.CharField(max_length=20, write_only=True)
    passport_issued_by = serializers.CharField(required=False, allow_blank=True)
    passport_issued_at = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Employee
        fields = (
            "id",
            "user",
            "full_name",
            "passport_series",
            "passport_number",
            "passport_issued_by",
            "passport_issued_at",
        )
        read_only_fields = ("id",)


class EmployeeDismissalSerializer(serializers.Serializer):
    ended_at = serializers.DateField()
    dismissal_reason = serializers.CharField(allow_blank=False, max_length=2000)


class ChickenWeightRecordSerializer(serializers.ModelSerializer):
    weight_grams = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=0)

    class Meta:
        model = ChickenWeightRecord
        fields = ("id", "chicken", "measured_at", "weight_grams")

    def validate(self, attrs):
        chicken = attrs.get("chicken", getattr(self.instance, "chicken", None))
        measured_at = attrs.get("measured_at", getattr(self.instance, "measured_at", None))
        if chicken and measured_at:
            if measured_at < chicken.arrived_at:
                raise serializers.ValidationError({"measured_at": "Взвешивание не может быть раньше прибытия курицы."})
            if chicken.removed_at and measured_at > chicken.removed_at:
                raise serializers.ValidationError({"measured_at": "Нельзя взвешивать курицу после выбытия."})
        return attrs


class ChickenWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chicken
        fields = ("id", "breed", "birth_date", "arrived_at", "removed_at", "removal_reason")
        read_only_fields = ("id",)

    def validate(self, attrs):
        birth_date = attrs.get("birth_date", getattr(self.instance, "birth_date", None))
        arrived_at = attrs.get("arrived_at", getattr(self.instance, "arrived_at", None))
        removed_at = attrs.get("removed_at", getattr(self.instance, "removed_at", None))
        removal_reason = attrs.get("removal_reason", getattr(self.instance, "removal_reason", None))
        if birth_date and arrived_at and birth_date > arrived_at:
            raise serializers.ValidationError({"birth_date": "Дата рождения должна предшествовать прибытию."})
        if removed_at and arrived_at and removed_at < arrived_at:
            raise serializers.ValidationError({"removed_at": "Дата выбытия не может быть раньше прибытия."})
        if removed_at and not removal_reason:
            raise serializers.ValidationError({"removal_reason": "Укажите причину выбытия курицы."})
        return attrs


class ChickenDetailSerializer(serializers.ModelSerializer):
    breed = BreedSerializer(read_only=True)
    current_assignment = serializers.SerializerMethodField()
    latest_weight_grams = serializers.SerializerMethodField()

    class Meta:
        model = Chicken
        fields = (
            "id",
            "breed",
            "birth_date",
            "arrived_at",
            "removed_at",
            "removal_reason",
            "current_assignment",
            "latest_weight_grams",
        )

    def get_current_assignment(self, obj):
        today = timezone.localdate()
        rows = getattr(obj, "current_cage_assignments", None)
        if rows is None:
            rows = obj.cage_assignments.filter(valid_from__lte=today).select_related("cage__workshop")
        assignment = next(
            (
                row
                for row in rows
                if row.valid_from <= today and (row.valid_to is None or row.valid_to >= today)
            ),
            None,
        )
        return ChickenAssignmentReadSerializer(assignment).data if assignment else None

    def get_latest_weight_grams(self, obj):
        weight = obj.weight_records.filter(measured_at__lte=timezone.localdate()).order_by("-measured_at").first()
        return weight.weight_grams if weight else None


class ChickenCageAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChickenCageAssignment
        fields = ("id", "chicken", "cage", "valid_from", "valid_to")
        read_only_fields = ("id",)

    def validate(self, attrs):
        chicken = attrs.get("chicken", getattr(self.instance, "chicken", None))
        cage = attrs.get("cage", getattr(self.instance, "cage", None))
        valid_from = attrs.get("valid_from", getattr(self.instance, "valid_from", None))
        valid_to = attrs.get("valid_to", getattr(self.instance, "valid_to", None))
        try:
            validate_chicken_cage_assignment(
                chicken=chicken,
                cage=cage,
                valid_from=valid_from,
                valid_to=valid_to,
                assignment_id=self.instance.pk if self.instance else None,
            )
        except DjangoValidationError as exc:
            _raise_api_validation_error(exc)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        try:
            validate_chicken_cage_assignment(**validated_data)
        except DjangoValidationError as exc:
            _raise_api_validation_error(exc)
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        values = {
            "chicken": validated_data.get("chicken", instance.chicken),
            "cage": validated_data.get("cage", instance.cage),
            "valid_from": validated_data.get("valid_from", instance.valid_from),
            "valid_to": validated_data.get("valid_to", instance.valid_to),
            "assignment_id": instance.pk,
        }
        try:
            validate_chicken_cage_assignment(**values)
        except DjangoValidationError as exc:
            _raise_api_validation_error(exc)
        return super().update(instance, validated_data)


class EmployeeCageAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeCageAssignment
        fields = ("id", "employee", "cage", "assigned_from", "assigned_to")
        read_only_fields = ("id",)

    def validate(self, attrs):
        values = {
            "employee": attrs.get("employee", getattr(self.instance, "employee", None)),
            "cage": attrs.get("cage", getattr(self.instance, "cage", None)),
            "assigned_from": attrs.get("assigned_from", getattr(self.instance, "assigned_from", None)),
            "assigned_to": attrs.get("assigned_to", getattr(self.instance, "assigned_to", None)),
            "assignment_id": self.instance.pk if self.instance else None,
        }
        try:
            validate_employee_cage_assignment(**values)
        except DjangoValidationError as exc:
            _raise_api_validation_error(exc)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        try:
            validate_employee_cage_assignment(**validated_data)
        except DjangoValidationError as exc:
            _raise_api_validation_error(exc)
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        new_cage = validated_data.get("cage", instance.cage)
        if new_cage.pk != instance.cage_id:
            try:
                validate_employee_assignment_removal(instance)
            except DjangoValidationError as exc:
                _raise_api_validation_error(exc)
        values = {
            "employee": validated_data.get("employee", instance.employee),
            "cage": validated_data.get("cage", instance.cage),
            "assigned_from": validated_data.get("assigned_from", instance.assigned_from),
            "assigned_to": validated_data.get("assigned_to", instance.assigned_to),
            "assignment_id": instance.pk,
        }
        try:
            validate_employee_cage_assignment(**values)
        except DjangoValidationError as exc:
            _raise_api_validation_error(exc)
        return super().update(instance, validated_data)


class EggProductionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EggProductionRecord
        fields = ("id", "chicken", "production_date", "eggs_count")

    def validate(self, attrs):
        chicken = attrs.get("chicken", getattr(self.instance, "chicken", None))
        production_date = attrs.get("production_date", getattr(self.instance, "production_date", None))
        if chicken and production_date:
            if production_date < chicken.arrived_at:
                raise serializers.ValidationError({"production_date": "Запись не может предшествовать прибытию курицы."})
            if chicken.removed_at and production_date > chicken.removed_at:
                raise serializers.ValidationError({"production_date": "Нельзя записать яйца после выбытия курицы."})
            has_cage = ChickenCageAssignment.objects.filter(
                chicken=chicken,
                valid_from__lte=production_date,
            ).filter(Q(valid_to__isnull=True) | Q(valid_to__gte=production_date)).exists()
            if not has_cage:
                raise serializers.ValidationError(
                    {"chicken": "Для учёта яиц у курицы должно быть назначение в клетку на эту дату."}
                )
        return attrs
