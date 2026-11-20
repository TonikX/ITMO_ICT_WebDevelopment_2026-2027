from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from .models import (
    Cage,
    Chicken,
    ChickenCageAssignment,
    ChickenRemovalReason,
    ChickenWeightRecord,
    EggProductionRecord,
    EmployeeCageAssignment,
)


def _interval_end(value):
    return value or date.max


def _covers(row, start_field, end_field, day):
    start = getattr(row, start_field)
    end = getattr(row, end_field)
    return start <= day and (end is None or end >= day)


def _critical_dates(start, end, intervals):
    upper = _interval_end(end)
    days = {start}
    for interval_start, interval_end in intervals:
        if start < interval_start <= upper:
            days.add(interval_start)
        if interval_end is not None and start <= interval_end < upper:
            days.add(interval_end + timedelta(days=1))
    return sorted(days)


def _overlap_filter(start, end, start_field, end_field):
    return Q(**{f"{start_field}__lte": _interval_end(end)}) & (
        Q(**{f"{end_field}__isnull": True}) | Q(**{f"{end_field}__gte": start})
    )


@transaction.atomic
def validate_chicken_cage_assignment(
    *, chicken, cage, valid_from, valid_to=None, assignment_id=None
):
    locked_cage = Cage.objects.select_for_update().get(pk=cage.pk)
    locked_chicken = Chicken.objects.select_for_update().get(pk=chicken.pk)

    if valid_to and valid_to < valid_from:
        raise ValidationError({"valid_to": "Дата окончания не может быть раньше даты начала."})
    if valid_from < locked_chicken.arrived_at:
        raise ValidationError({"valid_from": "Курицу нельзя назначить в клетку до прибытия на фабрику."})
    if locked_chicken.removed_at and (
        valid_to is None or valid_to > locked_chicken.removed_at or valid_from > locked_chicken.removed_at
    ):
        raise ValidationError({"valid_to": "Назначение не может продолжаться после выбытия курицы."})

    other_chicken_assignments = list(
        ChickenCageAssignment.objects.filter(chicken_id=locked_chicken.pk)
        .filter(_overlap_filter(valid_from, valid_to, "valid_from", "valid_to"))
        .exclude(pk=assignment_id)
    )
    if other_chicken_assignments:
        raise ValidationError("У курицы уже есть назначение на пересекающийся период.")

    cage_assignments = list(
        ChickenCageAssignment.objects.filter(cage_id=locked_cage.pk)
        .filter(_overlap_filter(valid_from, valid_to, "valid_from", "valid_to"))
        .exclude(pk=assignment_id)
        .select_related("chicken")
    )
    candidate = ChickenCageAssignment(
        chicken=locked_chicken,
        cage=locked_cage,
        valid_from=valid_from,
        valid_to=valid_to,
    )
    cage_assignments.append(candidate)

    staff_assignments = list(
        EmployeeCageAssignment.objects.filter(cage_id=locked_cage.pk)
        .filter(_overlap_filter(valid_from, valid_to, "assigned_from", "assigned_to"))
    )
    boundaries = [
        (row.valid_from, row.valid_to) for row in cage_assignments
    ] + [(row.assigned_from, row.assigned_to) for row in staff_assignments]

    for day in _critical_dates(valid_from, valid_to, boundaries):
        if not _covers(candidate, "valid_from", "valid_to", day):
            continue
        active_chickens = {
            row.chicken_id
            for row in cage_assignments
            if _covers(row, "valid_from", "valid_to", day)
            and row.chicken.arrived_at <= day
            and (row.chicken.removed_at is None or row.chicken.removed_at >= day)
        }
        if len(active_chickens) > locked_cage.capacity_chickens:
            raise ValidationError({"cage": "Превышена вместимость клетки по количеству кур."})

        has_employee = any(
            _covers(row, "assigned_from", "assigned_to", day) for row in staff_assignments
        )
        if not has_employee:
            raise ValidationError({"cage": "Клетка должна быть закреплена за работником на весь период."})


@transaction.atomic
def validate_employee_cage_assignment(
    *, employee, cage, assigned_from, assigned_to=None, assignment_id=None
):
    locked_cage = Cage.objects.select_for_update().get(pk=cage.pk)
    if assigned_to and assigned_to < assigned_from:
        raise ValidationError({"assigned_to": "Дата окончания не может быть раньше даты начала."})

    overlapping = EmployeeCageAssignment.objects.filter(
        employee_id=employee.pk,
        cage_id=locked_cage.pk,
    ).filter(_overlap_filter(assigned_from, assigned_to, "assigned_from", "assigned_to"))
    if assignment_id:
        overlapping = overlapping.exclude(pk=assignment_id)
    if overlapping.exists():
        raise ValidationError("Работник уже назначен на эту клетку в пересекающийся период.")

    staff_assignments = list(EmployeeCageAssignment.objects.filter(cage_id=locked_cage.pk).exclude(pk=assignment_id))
    staff_assignments.append(
        EmployeeCageAssignment(
            employee=employee,
            cage=locked_cage,
            assigned_from=assigned_from,
            assigned_to=assigned_to,
        )
    )
    chicken_assignments = list(
        ChickenCageAssignment.objects.filter(cage_id=locked_cage.pk).select_related("chicken")
    )

    intervals = [(row.assigned_from, row.assigned_to) for row in staff_assignments]
    intervals.append((assigned_from, assigned_to))
    intervals.extend((row.valid_from, row.valid_to) for row in chicken_assignments)
    starts = [interval_start for interval_start, _ in intervals]
    start = min(starts)
    has_open_chicken_assignment = any(row.valid_to is None for row in chicken_assignments)
    end = None if has_open_chicken_assignment else max(
        (interval_end for _, interval_end in intervals if interval_end is not None),
        default=assigned_to,
    )
    for day in _critical_dates(start, end, intervals):
        occupied = any(
            _covers(row, "valid_from", "valid_to", day)
            and row.chicken.arrived_at <= day
            and (row.chicken.removed_at is None or row.chicken.removed_at >= day)
            for row in chicken_assignments
        )
        if occupied and not any(
            _covers(row, "assigned_from", "assigned_to", day) for row in staff_assignments
        ):
            raise ValidationError({"assigned_to": "Нельзя оставить занятую клетку без работника."})


@transaction.atomic
def validate_employee_assignment_removal(assignment):
    cage = Cage.objects.select_for_update().get(pk=assignment.cage_id)
    staff_assignments = list(
        EmployeeCageAssignment.objects.filter(cage_id=cage.pk).exclude(pk=assignment.pk)
    )
    chicken_assignments = list(
        ChickenCageAssignment.objects.filter(cage_id=cage.pk).select_related("chicken")
    )
    intervals = [(row.assigned_from, row.assigned_to) for row in staff_assignments]
    intervals.extend((row.valid_from, row.valid_to) for row in chicken_assignments)
    if not intervals:
        return
    start = min(interval_start for interval_start, _ in intervals)
    has_open_chicken_assignment = any(row.valid_to is None for row in chicken_assignments)
    end = None if has_open_chicken_assignment else max(
        (interval_end for _, interval_end in intervals if interval_end is not None),
        default=start,
    )
    for day in _critical_dates(start, end, intervals):
        occupied = any(
            _covers(row, "valid_from", "valid_to", day)
            and row.chicken.arrived_at <= day
            and (row.chicken.removed_at is None or row.chicken.removed_at >= day)
            for row in chicken_assignments
        )
        if occupied and not any(
            _covers(row, "assigned_from", "assigned_to", day) for row in staff_assignments
        ):
            raise ValidationError("Нельзя удалить последнее закрепление для занятой клетки.")


def validate_workshop_cage_capacity(workshop, *, exclude_cage_id=None):
    cages = Cage.objects.filter(workshop_id=workshop.pk)
    if exclude_cage_id:
        cages = cages.exclude(pk=exclude_cage_id)
    if cages.count() >= workshop.capacity_cages:
        raise ValidationError({"workshop": "В цехе достигнута вместимость по числу клеток."})


def validate_cage_chicken_capacity(cage, *, capacity=None):
    from django.utils import timezone

    today = timezone.localdate()
    current_count = ChickenCageAssignment.objects.filter(
        cage_id=cage.pk,
        valid_from__lte=today,
    ).filter(Q(valid_to__isnull=True) | Q(valid_to__gte=today)).filter(
        Q(chicken__removed_at__isnull=True) | Q(chicken__removed_at__gte=today)
    ).filter(chicken__arrived_at__lte=today).values("chicken_id").distinct().count()
    allowed = capacity if capacity is not None else cage.capacity_chickens
    if current_count > allowed:
        raise ValidationError({"capacity_chickens": "Вместимость меньше числа кур, уже находящихся в клетке."})


@transaction.atomic
def remove_chicken(*, chicken, removed_at, removal_reason):
    locked_chicken = Chicken.objects.select_for_update().get(pk=chicken.pk)
    if removed_at < locked_chicken.arrived_at:
        raise ValidationError({"removed_at": "Дата выбытия не может быть раньше даты прибытия."})
    if removal_reason not in ChickenRemovalReason.values:
        raise ValidationError({"removal_reason": "Укажите допустимую причину выбытия."})
    if locked_chicken.removed_at and locked_chicken.removed_at != removed_at:
        raise ValidationError({"removed_at": "Дата выбытия уже установлена."})
    if EggProductionRecord.objects.filter(chicken=locked_chicken, production_date__gt=removed_at).exists():
        raise ValidationError({"removed_at": "Дата выбытия предшествует уже записанной яйценоскости."})
    if ChickenWeightRecord.objects.filter(chicken=locked_chicken, measured_at__gt=removed_at).exists():
        raise ValidationError({"removed_at": "Дата выбытия предшествует уже записанным измерениям веса."})

    current_assignment = (
        ChickenCageAssignment.objects.select_for_update()
        .filter(chicken=locked_chicken, valid_to__isnull=True)
        .first()
    )
    if current_assignment:
        if removed_at < current_assignment.valid_from:
            raise ValidationError({"removed_at": "Дата выбытия раньше даты назначения в клетку."})
        current_assignment.valid_to = removed_at
        current_assignment.save(update_fields=("valid_to",))

    locked_chicken.removed_at = removed_at
    locked_chicken.removal_reason = removal_reason
    locked_chicken.save(update_fields=("removed_at", "removal_reason"))
    return locked_chicken
