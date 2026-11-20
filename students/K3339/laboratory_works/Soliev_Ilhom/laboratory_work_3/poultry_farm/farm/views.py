from datetime import date

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import analytics
from .models import (
    Breed,
    BreedSeasonDiet,
    Cage,
    Chicken,
    ChickenCageAssignment,
    ChickenRemovalReason,
    ChickenWeightRecord,
    Diet,
    EggProductionRecord,
    Employee,
    EmployeeCageAssignment,
    EmploymentContract,
    Workshop,
)
from .permissions import DirectorOrReadOnly
from .serializers import (
    BreedSeasonDietSerializer,
    BreedSerializer,
    CageSerializer,
    ChickenCageAssignmentSerializer,
    ChickenDetailSerializer,
    ChickenWeightRecordSerializer,
    ChickenWriteSerializer,
    DietSerializer,
    EggProductionRecordSerializer,
    EmployeeCageAssignmentSerializer,
    EmployeeReadSerializer,
    EmployeeDismissalSerializer,
    EmployeeWriteSerializer,
    EmploymentContractSerializer,
    WorkshopSerializer,
)
from .services import (
    remove_chicken,
    validate_cage_chicken_capacity,
    validate_employee_cage_assignment,
    validate_employee_assignment_removal,
    validate_workshop_cage_capacity,
)


class ReadWriteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)


class WorkshopViewSet(ReadWriteViewSet):
    queryset = Workshop.objects.prefetch_related("cages__workshop").all()
    serializer_class = WorkshopSerializer

    def perform_update(self, serializer):
        with transaction.atomic():
            workshop = Workshop.objects.select_for_update().get(pk=serializer.instance.pk)
            capacity = serializer.validated_data.get("capacity_cages", workshop.capacity_cages)
            if workshop.cages.count() > capacity:
                raise ValidationError({"capacity_cages": "Вместимость не может быть меньше числа клеток в цехе."})
            serializer.save()


class CageViewSet(ReadWriteViewSet):
    queryset = Cage.objects.select_related("workshop").all()
    serializer_class = CageSerializer

    def perform_create(self, serializer):
        workshop = serializer.validated_data["workshop"]
        with transaction.atomic():
            locked_workshop = Workshop.objects.select_for_update().get(pk=workshop.pk)
            try:
                validate_workshop_cage_capacity(locked_workshop)
            except DjangoValidationError as exc:
                raise ValidationError(getattr(exc, "message_dict", exc.messages)) from exc
            cage = serializer.save()
            try:
                cage.full_clean()
            except DjangoValidationError as exc:
                raise ValidationError(getattr(exc, "message_dict", exc.messages)) from exc

    def perform_update(self, serializer):
        instance = serializer.instance
        workshop = serializer.validated_data.get("workshop", instance.workshop)
        with transaction.atomic():
            locked_cage = Cage.objects.select_for_update().get(pk=instance.pk)
            locked_workshop = Workshop.objects.select_for_update().get(pk=workshop.pk)
            if workshop.pk != instance.workshop_id:
                try:
                    validate_workshop_cage_capacity(locked_workshop, exclude_cage_id=instance.pk)
                except DjangoValidationError as exc:
                    raise ValidationError(getattr(exc, "message_dict", exc.messages)) from exc
            capacity = serializer.validated_data.get("capacity_chickens", locked_cage.capacity_chickens)
            try:
                validate_cage_chicken_capacity(locked_cage, capacity=capacity)
            except DjangoValidationError as exc:
                raise ValidationError(getattr(exc, "message_dict", exc.messages)) from exc
            cage = serializer.save()
            try:
                cage.full_clean()
            except DjangoValidationError as exc:
                raise ValidationError(getattr(exc, "message_dict", exc.messages)) from exc


class BreedViewSet(ReadWriteViewSet):
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer


class ChickenViewSet(ReadWriteViewSet):
    queryset = Chicken.objects.all()
    serializer_class = ChickenWriteSerializer

    def get_queryset(self):
        today = timezone.localdate()
        assignments = ChickenCageAssignment.objects.filter(valid_from__lte=today).filter(
            Q(valid_to__isnull=True) | Q(valid_to__gte=today)
        ).select_related("cage__workshop")
        weights = ChickenWeightRecord.objects.filter(measured_at__lte=today).order_by("-measured_at")
        return (
            Chicken.objects.select_related("breed")
            .prefetch_related(
                Prefetch("cage_assignments", queryset=assignments, to_attr="current_cage_assignments"),
                Prefetch("weight_records", queryset=weights, to_attr="available_weight_records"),
            )
            .all()
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ChickenWriteSerializer
        return ChickenDetailSerializer

    def perform_update(self, serializer):
        previous_removal_date = serializer.instance.removed_at
        with transaction.atomic():
            chicken = serializer.save()
            if previous_removal_date is None and chicken.removed_at is not None:
                try:
                    remove_chicken(
                        chicken=chicken,
                        removed_at=chicken.removed_at,
                        removal_reason=chicken.removal_reason,
                    )
                except DjangoValidationError as exc:
                    raise ValidationError(getattr(exc, "message_dict", exc.messages)) from exc

    @action(detail=True, methods=("post",), url_path="remove")
    def remove(self, request, pk=None):
        chicken = get_object_or_404(Chicken, pk=pk)
        input_serializer = ChickenRemovalSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            chicken = remove_chicken(
                chicken=chicken,
                removed_at=input_serializer.validated_data["removed_at"],
                removal_reason=input_serializer.validated_data["removal_reason"],
            )
        except DjangoValidationError as exc:
            raise ValidationError(getattr(exc, "message_dict", exc.messages)) from exc
        return Response(ChickenDetailSerializer(chicken).data)


class ChickenRemovalSerializer(serializers.Serializer):
    removed_at = serializers.DateField()
    removal_reason = serializers.ChoiceField(choices=ChickenRemovalReason.choices)


class ChickenWeightRecordViewSet(ReadWriteViewSet):
    queryset = ChickenWeightRecord.objects.select_related("chicken").all()
    serializer_class = ChickenWeightRecordSerializer


class ChickenCageAssignmentViewSet(ReadWriteViewSet):
    queryset = ChickenCageAssignment.objects.select_related("chicken", "cage__workshop").all()
    serializer_class = ChickenCageAssignmentSerializer


class EmployeeViewSet(ReadWriteViewSet):
    queryset = Employee.objects.select_related("user").prefetch_related(
        "contracts",
        "cage_assignments__cage__workshop",
    )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return EmployeeWriteSerializer
        return EmployeeReadSerializer

    def get_permissions(self):
        permission_class = DirectorOrReadOnly if self.action in {
            "create", "update", "partial_update", "destroy", "dismiss"
        } else IsAuthenticated
        return [permission_class()]

    @action(detail=True, methods=("post",), url_path="dismiss")
    def dismiss(self, request, pk=None):
        employee = get_object_or_404(Employee.objects.select_related("user"), pk=pk)
        input_serializer = EmployeeDismissalSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        ended_at = input_serializer.validated_data["ended_at"]
        dismissal_reason = input_serializer.validated_data["dismissal_reason"]

        with transaction.atomic():
            contracts = list(employee.contracts.select_for_update().filter(ended_at__isnull=True))
            if not contracts:
                raise ValidationError("У работника нет действующего трудового договора.")
            if any(ended_at < contract.started_at for contract in contracts):
                raise ValidationError("Дата увольнения не может быть раньше даты начала договора.")

            assignments = list(
                employee.cage_assignments.select_for_update().filter(assigned_to__isnull=True)
            )
            for assignment in assignments:
                try:
                    if assignment.assigned_from > ended_at:
                        validate_employee_assignment_removal(assignment)
                        assignment.delete()
                    else:
                        validate_employee_cage_assignment(
                            employee=employee,
                            cage=assignment.cage,
                            assigned_from=assignment.assigned_from,
                            assigned_to=ended_at,
                            assignment_id=assignment.pk,
                        )
                        assignment.assigned_to = ended_at
                        assignment.save(update_fields=("assigned_to",))
                except DjangoValidationError as exc:
                    raise ValidationError(getattr(exc, "message_dict", exc.messages)) from exc

            for contract in contracts:
                contract.ended_at = ended_at
                contract.dismissal_reason = dismissal_reason
                contract.save(update_fields=("ended_at", "dismissal_reason"))
            if employee.user_id and ended_at <= timezone.localdate():
                employee.user.is_active = False
                employee.user.save(update_fields=("is_active",))

        employee.refresh_from_db()
        return Response(EmployeeReadSerializer(employee).data)

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError as exc:
            raise ValidationError(
                "Нельзя удалить работника с договорами или историей назначений. Используйте /dismiss/."
            ) from exc


class EmploymentContractViewSet(ReadWriteViewSet):
    queryset = EmploymentContract.objects.select_related("employee").all()
    serializer_class = EmploymentContractSerializer

    def get_permissions(self):
        permission_class = DirectorOrReadOnly if self.action in {
            "create", "update", "partial_update", "destroy"
        } else IsAuthenticated
        return [permission_class()]


class EmployeeCageAssignmentViewSet(ReadWriteViewSet):
    queryset = EmployeeCageAssignment.objects.select_related("employee", "cage__workshop").all()
    serializer_class = EmployeeCageAssignmentSerializer

    def get_permissions(self):
        permission_class = DirectorOrReadOnly if self.action in {
            "create", "update", "partial_update", "destroy"
        } else IsAuthenticated
        return [permission_class()]

    @transaction.atomic
    def perform_destroy(self, instance):
        try:
            validate_employee_assignment_removal(instance)
        except DjangoValidationError as exc:
            raise ValidationError(getattr(exc, "message_dict", exc.messages)) from exc
        instance.delete()


class EggProductionRecordViewSet(ReadWriteViewSet):
    queryset = EggProductionRecord.objects.select_related("chicken__breed").all()
    serializer_class = EggProductionRecordSerializer


class DietViewSet(ReadWriteViewSet):
    queryset = Diet.objects.all()
    serializer_class = DietSerializer


class BreedSeasonDietViewSet(ReadWriteViewSet):
    queryset = BreedSeasonDiet.objects.select_related("breed", "diet").all()
    serializer_class = BreedSeasonDietSerializer


def _parse_int_param(value, name, *, minimum=0):
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Параметр {name} должен быть целым числом.") from exc
    if parsed < minimum:
        raise ValueError(f"Параметр {name} должен быть не меньше {minimum}.")
    return parsed


def _parse_decimal_param(value, name):
    if value in (None, ""):
        return None
    from decimal import Decimal, InvalidOperation

    try:
        parsed = Decimal(value)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"Параметр {name} должен быть числом.") from exc
    if not parsed.is_finite() or parsed < 0:
        raise ValueError(f"Параметр {name} не может быть отрицательным.")
    return parsed


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=("get",), url_path="chicken-eggs")
    def chicken_eggs(self, request):
        try:
            breed_id = _parse_int_param(request.query_params.get("breed_id"), "breed_id", minimum=1)
            weight_min = _parse_decimal_param(request.query_params.get("weight_min"), "weight_min")
            weight_max = _parse_decimal_param(request.query_params.get("weight_max"), "weight_max")
            age_min = _parse_int_param(request.query_params.get("age_min"), "age_min")
            age_max = _parse_int_param(request.query_params.get("age_max"), "age_max")
            if weight_min is not None and weight_max is not None and weight_min > weight_max:
                raise ValueError("weight_min не может быть больше weight_max.")
            if age_min is not None and age_max is not None and age_min > age_max:
                raise ValueError("age_min не может быть больше age_max.")
            data = analytics.chicken_egg_totals(
                month=request.query_params.get("month"),
                breed_id=breed_id,
                weight_min=weight_min,
                weight_max=weight_max,
                age_min=age_min,
                age_max=age_max,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)

    @action(detail=False, methods=("get",), url_path="top-workshop")
    def top_workshop(self, request):
        try:
            breed_id = _parse_int_param(request.query_params.get("breed_id"), "breed_id", minimum=1)
            if breed_id is None:
                raise ValueError("Укажите breed_id.")
            if not Breed.objects.filter(pk=breed_id).exists():
                return Response({"detail": "Порода не найдена."}, status=status.HTTP_404_NOT_FOUND)
            return Response(analytics.top_workshops_by_breed(breed_id=breed_id))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=("get",), url_path="worker-egg-average")
    def worker_egg_average(self, request):
        try:
            data = analytics.worker_egg_averages(
                date_from=request.query_params.get("date_from"),
                date_to=request.query_params.get("date_to"),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)

    @action(detail=False, methods=("get",), url_path="breed-workshop-counts")
    def breed_workshop_counts(self, request):
        return Response(analytics.breed_workshop_counts())

    @action(detail=False, methods=("get",), url_path="breed-comparison")
    def breed_comparison(self, request):
        try:
            return Response(analytics.breed_indicators_vs_farm(month=request.query_params.get("month")))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=("get",), url_path="monthly-report")
    def monthly_report(self, request):
        try:
            return Response(analytics.monthly_farm_report(month=request.query_params.get("month")))
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
