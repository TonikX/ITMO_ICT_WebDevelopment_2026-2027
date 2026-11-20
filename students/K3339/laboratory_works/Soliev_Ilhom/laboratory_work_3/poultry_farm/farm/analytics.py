from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Count, IntegerField, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import (
    Breed,
    Cage,
    Chicken,
    ChickenCageAssignment,
    ChickenWeightRecord,
    EggProductionRecord,
    Employee,
    EmployeeCageAssignment,
    Workshop,
)


CENT = Decimal("0.01")


def previous_month_range(month_value=None):
    if month_value:
        try:
            first = datetime.strptime(month_value, "%Y-%m").date().replace(day=1)
        except ValueError as exc:
            raise ValueError("Параметр month должен иметь формат YYYY-MM.") from exc
        if first.strftime("%Y-%m") != month_value:
            raise ValueError("Параметр month должен иметь формат YYYY-MM.")
    else:
        today = timezone.localdate()
        this_month = today.replace(day=1)
        first = this_month - timedelta(days=1)
        first = first.replace(day=1)

    if first.month == 12:
        next_month = date(first.year + 1, 1, 1)
    else:
        next_month = date(first.year, first.month + 1, 1)
    return first, next_month - timedelta(days=1)


def parse_date_range(date_from=None, date_to=None):
    date_from = date_from or None
    date_to = date_to or None
    if date_from is None and date_to is None:
        return previous_month_range()
    try:
        start = date.fromisoformat(date_from) if date_from else date_to_date(date_to)
        end = date.fromisoformat(date_to) if date_to else start
    except (TypeError, ValueError) as exc:
        raise ValueError("Даты должны иметь формат YYYY-MM-DD.") from exc
    if end < start:
        raise ValueError("date_to не может быть раньше date_from.")
    if (end - start).days > 365:
        raise ValueError("Период аналитики не должен превышать 366 дней.")
    return start, end


def date_to_date(value):
    if value is None:
        return None
    return date.fromisoformat(value)


def chicken_age_on(birth_date, on_date):
    return on_date.year - birth_date.year - (
        (on_date.month, on_date.day) < (birth_date.month, birth_date.day)
    )


def _assignment_active(assignment, day):
    return assignment.valid_from <= day and (assignment.valid_to is None or assignment.valid_to >= day)


def _employee_assignment_active(assignment, day):
    return assignment.assigned_from <= day and (
        assignment.assigned_to is None or assignment.assigned_to >= day
    )


def chicken_egg_totals(*, month, breed_id=None, weight_min=None, weight_max=None, age_min=None, age_max=None):
    start, end = previous_month_range(month)
    latest_weight = ChickenWeightRecord.objects.filter(
        chicken_id=OuterRef("pk"),
        measured_at__lte=end,
    ).order_by("-measured_at").values("weight_grams")[:1]
    chickens = (
        Chicken.objects.filter(arrived_at__lte=end)
        .filter(Q(removed_at__isnull=True) | Q(removed_at__gte=start))
        .select_related("breed")
        .annotate(
            month_eggs=Coalesce(
                Sum(
                    "egg_records__eggs_count",
                    filter=Q(egg_records__production_date__gte=start)
                    & Q(egg_records__production_date__lte=end),
                ),
                Value(0),
                output_field=IntegerField(),
            ),
            latest_weight_grams=Subquery(latest_weight),
        )
    )
    if breed_id is not None:
        chickens = chickens.filter(breed_id=breed_id)
    if weight_min is not None:
        chickens = chickens.filter(latest_weight_grams__gte=weight_min)
    if weight_max is not None:
        chickens = chickens.filter(latest_weight_grams__lte=weight_max)

    results = []
    for chicken in chickens.order_by("id"):
        age = chicken_age_on(chicken.birth_date, end)
        if age_min is not None and age < age_min:
            continue
        if age_max is not None and age > age_max:
            continue
        results.append(
            {
                "chicken_id": chicken.pk,
                "breed": {"id": chicken.breed_id, "name": chicken.breed.name},
                "age_years": age,
                "weight_grams": chicken.latest_weight_grams,
                "eggs_count": chicken.month_eggs,
            }
        )
    return {"month": start.strftime("%Y-%m"), "results": results}


def top_workshops_by_breed(*, breed_id):
    today = timezone.localdate()
    counts = (
        ChickenCageAssignment.objects.filter(
            chicken__breed_id=breed_id,
            chicken__arrived_at__lte=today,
            valid_from__lte=today,
        )
        .filter(Q(valid_to__isnull=True) | Q(valid_to__gte=today))
        .filter(Q(chicken__removed_at__isnull=True) | Q(chicken__removed_at__gte=today))
        .values("cage__workshop_id", "cage__workshop__workshop_number", "cage__workshop__name")
        .annotate(chicken_count=Count("chicken_id", distinct=True))
        .order_by("-chicken_count", "cage__workshop__workshop_number")
    )
    rows = list(counts)
    maximum = rows[0]["chicken_count"] if rows else 0
    leaders = [
        {
            "workshop_id": row["cage__workshop_id"],
            "workshop_number": row["cage__workshop__workshop_number"],
            "name": row["cage__workshop__name"],
            "chicken_count": row["chicken_count"],
        }
        for row in rows
        if row["chicken_count"] == maximum
    ]
    breed = Breed.objects.only("id", "name").get(pk=breed_id)
    return {"breed": {"id": breed.pk, "name": breed.name}, "max_chickens": maximum, "workshops": leaders}


def worker_egg_averages(*, date_from=None, date_to=None):
    start, end = parse_date_range(date_from, date_to)
    records = list(
        EggProductionRecord.objects.filter(production_date__range=(start, end))
        .select_related("chicken")
        .order_by("production_date", "id")
    )
    chicken_ids = {record.chicken_id for record in records}
    chicken_assignments = list(
        ChickenCageAssignment.objects.filter(chicken_id__in=chicken_ids)
        .filter(Q(valid_from__lte=end) & (Q(valid_to__isnull=True) | Q(valid_to__gte=start)))
        .select_related("chicken", "cage")
    )
    cage_ids = {assignment.cage_id for assignment in chicken_assignments}
    employee_assignments = list(
        EmployeeCageAssignment.objects.filter(cage_id__in=cage_ids)
        .filter(Q(assigned_from__lte=end) & (Q(assigned_to__isnull=True) | Q(assigned_to__gte=start)))
        .select_related("employee")
    )
    chicken_assignments_by_chicken = defaultdict(list)
    for assignment in chicken_assignments:
        chicken_assignments_by_chicken[assignment.chicken_id].append(assignment)
    employee_assignments_by_cage = defaultdict(list)
    for assignment in employee_assignments:
        employee_assignments_by_cage[assignment.cage_id].append(assignment)

    allocated_eggs = defaultdict(Decimal)
    active_days = defaultdict(set)
    for assignment in employee_assignments:
        first = max(start, assignment.assigned_from)
        last = min(end, assignment.assigned_to or end)
        day = first
        while day <= last:
            active_days[assignment.employee_id].add(day)
            day += timedelta(days=1)

    for record in records:
        day = record.production_date
        chicken = record.chicken
        if chicken.arrived_at > day or (chicken.removed_at and chicken.removed_at < day):
            continue
        assignment = next(
            (row for row in chicken_assignments_by_chicken[record.chicken_id] if _assignment_active(row, day)),
            None,
        )
        if assignment is None:
            continue
        workers = {
            row.employee_id
            for row in employee_assignments_by_cage[assignment.cage_id]
            if _employee_assignment_active(row, day)
        }
        if not workers:
            continue
        share = Decimal(record.eggs_count) / Decimal(len(workers))
        for employee_id in workers:
            allocated_eggs[employee_id] += share

    employees = {
        employee.pk: employee
        for employee in Employee.objects.filter(pk__in=active_days).order_by("full_name", "id")
    }
    results = []
    for employee_id, employee in employees.items():
        days_count = len(active_days[employee_id])
        eggs = allocated_eggs[employee_id]
        results.append(
            {
                "employee_id": employee_id,
                "full_name": employee.full_name,
                "allocated_eggs": eggs.quantize(CENT, rounding=ROUND_HALF_UP),
                "assigned_days": days_count,
                "average_eggs_per_day": (eggs / days_count).quantize(CENT, rounding=ROUND_HALF_UP)
                if days_count
                else Decimal("0.00"),
            }
        )
    return {"date_from": start, "date_to": end, "results": results}


def breed_workshop_counts():
    today = timezone.localdate()
    rows = (
        ChickenCageAssignment.objects.filter(
            valid_from__lte=today,
            chicken__arrived_at__lte=today,
        )
        .filter(Q(valid_to__isnull=True) | Q(valid_to__gte=today))
        .filter(Q(chicken__removed_at__isnull=True) | Q(chicken__removed_at__gte=today))
        .values(
            "cage__workshop_id",
            "cage__workshop__workshop_number",
            "cage__workshop__name",
            "chicken__breed_id",
            "chicken__breed__name",
        )
        .annotate(chicken_count=Count("chicken_id", distinct=True))
        .order_by("cage__workshop__workshop_number", "chicken__breed__name")
    )
    return [
        {
            "workshop_id": row["cage__workshop_id"],
            "workshop_number": row["cage__workshop__workshop_number"],
            "workshop_name": row["cage__workshop__name"],
            "breed_id": row["chicken__breed_id"],
            "breed_name": row["chicken__breed__name"],
            "chicken_count": row["chicken_count"],
        }
        for row in rows
    ]


def breed_indicators_vs_farm(*, month=None):
    start, end = previous_month_range(month)
    latest_weight = ChickenWeightRecord.objects.filter(
        chicken_id=OuterRef("pk"),
        measured_at__lte=end,
    ).order_by("-measured_at").values("weight_grams")[:1]
    active_chickens = list(
        Chicken.objects.filter(arrived_at__lte=end)
        .filter(Q(removed_at__isnull=True) | Q(removed_at__gte=end))
        .select_related("breed")
        .annotate(latest_weight_grams=Subquery(latest_weight))
    )
    chicken_ids = [chicken.pk for chicken in active_chickens]
    egg_totals = dict(
        EggProductionRecord.objects.filter(
            chicken_id__in=chicken_ids,
            production_date__range=(start, end),
        )
        .values("chicken__breed_id")
        .annotate(total=Coalesce(Sum("eggs_count"), Value(0), output_field=IntegerField()))
        .values_list("chicken__breed_id", "total")
    )
    chicken_counts = defaultdict(int)
    weights_by_breed = defaultdict(list)
    for chicken in active_chickens:
        chicken_counts[chicken.breed_id] += 1
        if chicken.latest_weight_grams is not None:
            weights_by_breed[chicken.breed_id].append(Decimal(chicken.latest_weight_grams))

    total_chickens = len(active_chickens)
    farm_eggs_average = Decimal(sum(egg_totals.values())) / total_chickens if total_chickens else Decimal(0)
    all_weights = [
        Decimal(chicken.latest_weight_grams)
        for chicken in active_chickens
        if chicken.latest_weight_grams is not None
    ]
    farm_weight_average = sum(all_weights, Decimal(0)) / len(all_weights) if all_weights else None

    results = []
    for breed in Breed.objects.order_by("name"):
        count = chicken_counts[breed.pk]
        eggs = egg_totals.get(breed.pk, 0)
        breed_weight = (
            sum(weights_by_breed[breed.pk], Decimal(0)) / len(weights_by_breed[breed.pk])
            if weights_by_breed[breed.pk]
            else None
        )
        results.append(
            {
                "breed_id": breed.pk,
                "breed_name": breed.name,
                "chicken_count": count,
                "actual_eggs_per_chicken": (Decimal(eggs) / count).quantize(CENT, rounding=ROUND_HALF_UP)
                if count
                else None,
                "actual_average_weight_grams": breed_weight.quantize(CENT, rounding=ROUND_HALF_UP)
                if breed_weight is not None
                else None,
                "breed_average_eggs_per_month": breed.average_eggs_per_month,
                "farm_average_eggs_per_chicken": farm_eggs_average.quantize(CENT, rounding=ROUND_HALF_UP),
                "egg_indicator_difference": (
                    Decimal(breed.average_eggs_per_month) - farm_eggs_average
                ).quantize(CENT, rounding=ROUND_HALF_UP),
                "breed_average_weight_grams": breed.average_weight_grams,
                "farm_average_weight_grams": farm_weight_average.quantize(CENT, rounding=ROUND_HALF_UP)
                if farm_weight_average is not None
                else None,
                "weight_indicator_difference_grams": (
                    Decimal(breed.average_weight_grams) - farm_weight_average
                ).quantize(CENT, rounding=ROUND_HALF_UP)
                if farm_weight_average is not None
                else None,
            }
        )
    return {"month": start.strftime("%Y-%m"), "results": results}


def monthly_farm_report(*, month=None):
    start, end = previous_month_range(month)
    egg_records = list(
        EggProductionRecord.objects.filter(production_date__range=(start, end))
        .select_related("chicken__breed")
        .order_by("production_date", "id")
    )
    chicken_ids = {record.chicken_id for record in egg_records}
    assignments = list(
        ChickenCageAssignment.objects.filter(chicken_id__in=chicken_ids)
        .filter(Q(valid_from__lte=end) & (Q(valid_to__isnull=True) | Q(valid_to__gte=start)))
        .select_related("cage__workshop", "chicken__breed")
    )
    by_chicken = defaultdict(list)
    for assignment in assignments:
        by_chicken[assignment.chicken_id].append(assignment)

    eggs_by_group = defaultdict(int)
    total_eggs = 0
    for record in egg_records:
        total_eggs += record.eggs_count
        assignment = next(
            (row for row in by_chicken[record.chicken_id] if _assignment_active(row, record.production_date)),
            None,
        )
        if assignment:
            eggs_by_group[(assignment.cage.workshop_id, record.chicken.breed_id)] += record.eggs_count

    end_assignments = list(
        ChickenCageAssignment.objects.filter(
            valid_from__lte=end,
            chicken__arrived_at__lte=end,
        )
        .filter(Q(valid_to__isnull=True) | Q(valid_to__gte=end))
        .filter(Q(chicken__removed_at__isnull=True) | Q(chicken__removed_at__gte=end))
        .select_related("cage__workshop", "chicken__breed")
    )
    chickens_by_group = defaultdict(set)
    for assignment in end_assignments:
        chickens_by_group[(assignment.cage.workshop_id, assignment.chicken.breed_id)].add(
            assignment.chicken_id
        )
    total_chickens = len({assignment.chicken_id for assignment in end_assignments})

    grouped_keys = set(eggs_by_group) | set(chickens_by_group)
    breeds_by_id = {breed.pk: breed for breed in Breed.objects.all()}
    workshops = []
    for workshop in Workshop.objects.order_by("workshop_number"):
        breed_rows = []
        for workshop_id, breed_id in sorted(
            (key for key in grouped_keys if key[0] == workshop.pk),
            key=lambda key: breeds_by_id[key[1]].name,
        ):
            breed = breeds_by_id[breed_id]
            eggs = eggs_by_group[(workshop_id, breed_id)]
            chicken_count = len(chickens_by_group[(workshop_id, breed_id)])
            breed_rows.append(
                {
                    "breed_id": breed_id,
                    "breed_name": breed.name,
                    "chicken_count": chicken_count,
                    "eggs_count": eggs,
                    "average_eggs_per_chicken": (Decimal(eggs) / chicken_count).quantize(
                        CENT, rounding=ROUND_HALF_UP
                    )
                    if chicken_count
                    else None,
                }
            )
        workshops.append(
            {
                "workshop_id": workshop.pk,
                "workshop_number": workshop.workshop_number,
                "name": workshop.name,
                "breeds": breed_rows,
                "chicken_count": sum(row["chicken_count"] for row in breed_rows),
                "eggs_count": sum(row["eggs_count"] for row in breed_rows),
            }
        )
    return {
        "month": start.strftime("%Y-%m"),
        "date_from": start,
        "date_to": end,
        "workshops": workshops,
        "totals": {"chicken_count": total_chickens, "eggs_count": total_eggs},
    }
