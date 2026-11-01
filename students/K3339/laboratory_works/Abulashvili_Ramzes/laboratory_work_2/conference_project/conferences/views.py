from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegistrationForm, ResultForm, ReviewForm, SignUpForm
from .models import Conference, Registration, Review, Topic


def conference_list(request):
    conferences = Conference.objects.select_related("venue").prefetch_related("topics")
    query = request.GET.get("q", "").strip()
    topic = request.GET.get("topic", "")
    city = request.GET.get("city", "")
    if query:
        conferences = conferences.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if topic.isdigit():
        conferences = conferences.filter(topics__pk=topic)
    if city:
        conferences = conferences.filter(venue__city=city)
    page = Paginator(conferences.distinct(), 4).get_page(request.GET.get("page"))
    filters = request.GET.copy()
    filters.pop("page", None)
    cities = Conference.objects.values_list("venue__city", flat=True).distinct().order_by("venue__city")
    return render(request, "conferences/list.html", {
        "page": page, "topics": Topic.objects.all(), "cities": cities,
        "query": query, "selected_topic": topic, "selected_city": city, "filters": filters.urlencode(),
    })


def conference_detail(request, pk):
    conference = get_object_or_404(Conference.objects.select_related("venue").prefetch_related("topics"), pk=pk)
    registration = None
    review = None
    if request.user.is_authenticated:
        registration = conference.registrations.filter(author=request.user).first()
        review = conference.reviews.filter(author=request.user).first()
    return render(request, "conferences/detail.html", {
        "conference": conference, "registration": registration, "my_review": review,
        "reviews": conference.reviews.select_related("author"),
    })


def sign_up(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Аккаунт создан. Теперь можно подать заявку на выступление.")
        return redirect("conference_list")
    return render(request, "form.html", {"form": form, "title": "Регистрация", "button": "Создать аккаунт"})


@login_required
def my_registrations(request):
    registrations = request.user.registrations.select_related("conference", "conference__venue")
    return render(request, "conferences/my_registrations.html", {"registrations": registrations})


@login_required
def registration_create(request, pk):
    conference = get_object_or_404(Conference, pk=pk)
    existing = conference.registrations.filter(author=request.user).first()
    if existing:
        return redirect("registration_edit", pk=existing.pk)
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        registration = form.save(commit=False)
        registration.author = request.user
        registration.conference = conference
        registration.save()
        messages.success(request, "Заявка на выступление сохранена.")
        return redirect("my_registrations")
    return render(request, "form.html", {"form": form, "title": "Заявка на выступление", "subtitle": conference.title})


@login_required
def registration_edit(request, pk):
    registration = get_object_or_404(Registration, pk=pk, author=request.user)
    form = RegistrationForm(request.POST or None, instance=registration)
    if request.method == "POST" and form.is_valid():
        registration = form.save(commit=False)
        registration.result = Registration.Result.PENDING
        registration.save()
        messages.success(request, "Заявка обновлена и ожидает решения по новому содержанию.")
        return redirect("my_registrations")
    return render(request, "form.html", {"form": form, "title": "Редактирование заявки", "subtitle": registration.conference.title})


@login_required
def registration_delete(request, pk):
    registration = get_object_or_404(Registration, pk=pk, author=request.user)
    if request.method == "POST":
        registration.delete()
        messages.success(request, "Заявка удалена.")
        return redirect("my_registrations")
    return render(request, "conferences/delete.html", {"registration": registration})


@login_required
def review_edit(request, pk):
    conference = get_object_or_404(Conference, pk=pk)
    review = Review.objects.filter(conference=conference, author=request.user).first()
    form = ReviewForm(request.POST or None, instance=review)
    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        if not review.pk:
            review.author = request.user
            review.conference = conference
            review.conference_start = conference.start_date
            review.conference_end = conference.end_date
        review.save()
        messages.success(request, "Отзыв сохранён.")
        return redirect("conference_detail", pk=conference.pk)
    return render(request, "form.html", {"form": form, "title": "Отзыв о конференции", "subtitle": conference.title})


def participants(request):
    registrations = Registration.objects.select_related("conference", "author").order_by("conference__start_date", "conference_id", "author__last_name", "pk")
    conference_id = request.GET.get("conference", "")
    if conference_id.isdigit():
        registrations = registrations.filter(conference_id=conference_id)
    return render(request, "conferences/participants.html", {
        "registrations": registrations, "conferences": Conference.objects.all(), "selected_conference": conference_id,
    })


@login_required
def staff_registrations(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    registrations = Registration.objects.select_related("conference", "author")
    conference_id = request.GET.get("conference", "")
    result = request.GET.get("result", "")
    if conference_id.isdigit():
        registrations = registrations.filter(conference_id=conference_id)
    if result in Registration.Result.values:
        registrations = registrations.filter(result=result)
    return render(request, "conferences/staff.html", {
        "registrations": registrations, "conferences": Conference.objects.all(), "results": Registration.Result.choices,
        "selected_conference": conference_id, "selected_result": result,
    })


@login_required
def result_edit(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    registration = get_object_or_404(Registration.objects.select_related("conference", "author"), pk=pk)
    form = ResultForm(request.POST or None, instance=registration)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Результат выступления сохранён.")
        return redirect("staff_registrations")
    return render(request, "form.html", {
        "form": form, "title": "Результат выступления",
        "subtitle": f"{registration.author.get_full_name()} — {registration.presentation_title}",
    })
