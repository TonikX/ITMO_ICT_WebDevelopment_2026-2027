"""Бизнес-логика: выборки, сортировка, регистрация авторов.
Не знает про HTTP и принимает уже проверенные фильтры (см. формы-фильтры в forms.py)."""
from django.db.models import Avg, Count, F, Q

from .models import Conference, Participation, Topic

# Сортировка по белому списку: произвольный ?sort= в order_by не попадает.
SORT_OPTIONS = {
    "date": ("Сначала ближайшие", ("start_date", "title")),
    "-date": ("Сначала поздние", ("-start_date", "title")),
    "title": ("По названию", ("title",)),
    "rating": ("По рейтингу", (F("avg_rating").desc(nulls_last=True), "title")),
    "participants": ("По числу докладов", ("-participants_count", "title")),
}
DEFAULT_SORT = "date"

# фильтр формы -> условие выборки
CONFERENCE_LOOKUPS = {
    "topic": "topics",
    "city": "city__iexact",
    "date_from": "end_date__gte",
    "date_to": "start_date__lte",
}


def search_conferences(filters):
    """Конференции с поиском по `q`, условиями из CONFERENCE_LOOKUPS и сортировкой `sort`."""
    qs = Conference.objects.prefetch_related("topics").annotate(
        avg_rating=Avg("reviews__rating"), participants_count=Count("participations", distinct=True)
    )
    q = filters.get("q")
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(venue_name__icontains=q)
            | Q(topics__name__icontains=q)
        ).distinct()
    for name, lookup in CONFERENCE_LOOKUPS.items():
        if filters.get(name):
            qs = qs.filter(**{lookup: filters[name]})
    return qs.order_by(*SORT_OPTIONS[filters.get("sort") or DEFAULT_SORT][1])


def filter_options():
    """Варианты для выпадающих списков формы поиска."""
    return {
        "topics": Topic.objects.all(),
        "cities": Conference.objects.order_by("city").values_list("city", flat=True).distinct(),
        "sort_options": [(key, label) for key, (label, _) in SORT_OPTIONS.items()],
    }


def querystring_without_page(params):
    """Параметры поиска для ссылок пагинации: без `page`, иначе фильтр пропадёт на другой странице."""
    query = params.copy()
    query.pop("page", None)
    return query.urlencode()


def average_rating(conference):
    return conference.reviews.aggregate(avg=Avg("rating"))["avg"]


def get_participation(conference, user):
    if not user.is_authenticated:
        return None
    return Participation.objects.filter(conference=conference, user=user).first()


def register_author(conference, user, talk_title, abstract):
    """Одна регистрация на автора и конференцию. Возвращает (регистрация, создана_ли).
    `get_or_create` вместе с UniqueConstraint не даст создать дубль даже при гонке запросов."""
    return Participation.objects.get_or_create(
        conference=conference, user=user, defaults={"talk_title": talk_title, "abstract": abstract}
    )


def filter_participations(filters):
    """Участники: условия `conference` и `result`, поиск `q` по ФИО, организации и названию доклада."""
    qs = Participation.objects.all()
    if filters.get("conference"):
        qs = qs.filter(conference=filters["conference"])
    if filters.get("result"):
        qs = qs.filter(result=filters["result"])
    q = filters.get("q")
    if q:
        qs = qs.filter(
            Q(user__username__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(user__organization__icontains=q)
            | Q(talk_title__icontains=q)
        )
    return qs


def conferences_with_participants(participations):
    """Конференции, у которых есть подходящие участники, в порядке проведения."""
    return Conference.objects.filter(pk__in=participations.values("conference_id")).order_by("start_date", "title")


def group_by_conference(conferences, participations):
    """[(конференция, [участники])] для переданных конференций; строки упорядочены по фамилии."""
    rows = {conference.pk: [] for conference in conferences}
    ordered = participations.filter(conference__in=list(conferences)).select_related("user").order_by(
        "user__last_name", "user__username"
    )
    for participation in ordered:
        rows[participation.conference_id].append(participation)
    return [(conference, rows[conference.pk]) for conference in conferences]
