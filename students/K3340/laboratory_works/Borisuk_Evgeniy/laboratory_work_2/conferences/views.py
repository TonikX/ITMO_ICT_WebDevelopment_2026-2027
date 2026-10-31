"""Пользовательские интерфейсы конференций."""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RegistrationForm, ResultForm, ReviewForm, SignupForm
from .models import Conference, Registration, Topic


@require_POST
def logout_user(request: HttpRequest) -> HttpResponse:
    """Завершает сессию только запросом POST с проверкой CSRF."""
    logout(request)
    return redirect("conference_list")


def filter_id(value: str) -> int | None:
    """Принимает только положительный ASCII-идентификатор PostgreSQL bigint."""
    if not value.isascii() or not value.isdecimal() or len(value) > 19:
        return None
    identifier = int(value)
    return identifier if 0 < identifier <= 9223372036854775807 else None


def signup(request: HttpRequest) -> HttpResponse:
    """Регистрирует посетителя и начинает сессию."""
    form = SignupForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("conference_list")
    return render(
        request, "form.html", {"form": form, "title": "Регистрация пользователя"}
    )


def conference_list(request: HttpRequest) -> HttpResponse:
    """Показывает каталог с поиском, фильтрацией и пагинацией."""
    conferences = Conference.objects.prefetch_related("topics")
    query = request.GET.get("q", "").strip()
    topic = request.GET.get("topic", "")
    if query:
        conferences = conferences.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(location__icontains=query)
        )
    topic_id = filter_id(topic)
    if topic_id is not None:
        conferences = conferences.filter(topics__pk=topic_id)
    page = Paginator(conferences, 6).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(
        request,
        "conference_list.html",
        {
            "page": page,
            "topics": Topic.objects.all(),
            "query": query,
            "selected_topic": topic,
            "pagination_query": params.urlencode(),
        },
    )


def conference_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Показывает сведения, отзывы и регистрацию текущего автора."""
    conference = get_object_or_404(Conference.objects.prefetch_related("topics"), pk=pk)
    registration = None
    if request.user.is_authenticated:
        registration = conference.registrations.filter(author=request.user).first()
    return render(
        request,
        "conference_detail.html",
        {
            "conference": conference,
            "registration": registration,
            "reviews": conference.reviews.select_related("author"),
        },
    )


@login_required
def registration_create(request: HttpRequest, pk: int) -> HttpResponse:
    """Регистрирует автора на выбранную конференцию."""
    conference = get_object_or_404(Conference, pk=pk)
    if Registration.objects.filter(conference=conference, author=request.user).exists():
        messages.info(request, "Вы уже зарегистрированы на эту конференцию.")
        return redirect("conference_detail", pk=pk)
    form = RegistrationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        registration = form.save(commit=False)
        registration.conference = conference
        registration.author = request.user
        try:
            with transaction.atomic():
                registration.save()
        except IntegrityError:
            form.add_error(None, "Вы уже зарегистрированы на эту конференцию.")
        else:
            return redirect("conference_detail", pk=pk)
    return render(
        request,
        "form.html",
        {"form": form, "title": f"Выступление: {conference.title}"},
    )


@login_required
def registration_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """Редактирует собственное выступление, сбрасывая прежний результат."""
    registration = get_object_or_404(Registration, pk=pk, author=request.user)
    form = RegistrationForm(
        request.POST if request.method == "POST" else None, instance=registration
    )
    if request.method == "POST" and form.is_valid():
        if form.has_changed():
            registration.result = Registration.Result.PENDING
        form.save()
        return redirect("conference_detail", pk=registration.conference_id)
    return render(
        request, "form.html", {"form": form, "title": "Редактировать выступление"}
    )


@login_required
def registration_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Удаляет собственную регистрацию после подтверждения POST."""
    registration = get_object_or_404(Registration, pk=pk, author=request.user)
    if request.method == "POST":
        conference_id = registration.conference_id
        registration.delete()
        return redirect("conference_detail", pk=conference_id)
    return render(request, "confirm_delete.html", {"object": registration})


@login_required
def review_create(request: HttpRequest, pk: int) -> HttpResponse:
    """Сохраняет отзыв и даты конференции на момент написания."""
    conference = get_object_or_404(Conference, pk=pk)
    form = ReviewForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        review.conference = conference
        review.start_date = conference.start_date
        review.end_date = conference.end_date
        review.save()
        return redirect("conference_detail", pk=pk)
    return render(
        request, "form.html", {"form": form, "title": f"Отзыв: {conference.title}"}
    )


@login_required
def participants(request: HttpRequest) -> HttpResponse:
    """Показывает таблицу участников по конференциям."""
    if not request.user.is_staff:
        raise PermissionDenied
    registrations = Registration.objects.select_related("conference", "author")
    conference = request.GET.get("conference", "")
    conference_id = filter_id(conference)
    if conference_id is not None:
        registrations = registrations.filter(conference_id=conference_id)
    return render(
        request,
        "participants.html",
        {
            "registrations": registrations,
            "conferences": Conference.objects.all(),
            "selected_conference": conference,
        },
    )


@login_required
def result_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """Позволяет администратору указать результат в клиентском интерфейсе."""
    if not request.user.is_staff:
        raise PermissionDenied
    registration = get_object_or_404(Registration, pk=pk)
    form = ResultForm(
        request.POST if request.method == "POST" else None, instance=registration
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("participants")
    return render(
        request,
        "form.html",
        {"form": form, "title": f"Результат: {registration.presentation_title}"},
    )
