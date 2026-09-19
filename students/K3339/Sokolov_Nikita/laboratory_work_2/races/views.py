from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RaceCommentForm, RaceEntryForm, RaceResultForm, RegisterForm
from .models import Race, RaceEntry, RaceResult


def staff_required(view):
    return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view)


class UserLoginView(LoginView):
    template_name = "races/login.html"


class UserLogoutView(LogoutView):
    next_page = "race_list"


def register(request):
    if request.user.is_authenticated:
        return redirect("race_list")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("race_list")
    return render(request, "races/register.html", {"form": form})


def race_list(request):
    q = request.GET.get("q", "").strip()
    races = Race.objects.all()
    if q:
        races = races.filter(
            Q(title__icontains=q) | Q(location__icontains=q) | Q(description__icontains=q)
        )
    page = Paginator(races, 5).get_page(request.GET.get("page"))
    return render(request, "races/race_list.html", {"page": page, "q": q})


def race_detail(request, pk):
    race = get_object_or_404(Race, pk=pk)
    entries = race.entries.select_related("user", "result")
    comments = race.comments.select_related("author")
    my_entry = None
    if request.user.is_authenticated:
        my_entry = race.entries.filter(user=request.user).first()
    comment_form = RaceCommentForm(initial={"race_date": race.date})
    return render(
        request,
        "races/race_detail.html",
        {
            "race": race,
            "entries": entries,
            "comments": comments,
            "my_entry": my_entry,
            "comment_form": comment_form,
        },
    )


@login_required
def entry_create(request, race_id):
    race = get_object_or_404(Race, pk=race_id)
    if race.entries.filter(user=request.user).exists():
        return redirect("race_detail", pk=race.pk)
    form = RaceEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.race = race
        entry.user = request.user
        entry.save()
        return redirect("race_detail", pk=race.pk)
    return render(request, "races/entry_form.html", {"form": form, "race": race, "title": "Регистрация на гонку"})


@login_required
def entry_edit(request, pk):
    entry = get_object_or_404(RaceEntry, pk=pk)
    if entry.user != request.user and not request.user.is_staff:
        return redirect("race_detail", pk=entry.race_id)
    form = RaceEntryForm(request.POST or None, instance=entry)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("race_detail", pk=entry.race_id)
    return render(request, "races/entry_form.html", {"form": form, "race": entry.race, "title": "Редактирование заявки"})


@login_required
@require_POST
def entry_delete(request, pk):
    entry = get_object_or_404(RaceEntry, pk=pk)
    race_id = entry.race_id
    if entry.user == request.user or request.user.is_staff:
        entry.delete()
    return redirect("race_detail", pk=race_id)


@login_required
def comment_create(request, race_id):
    race = get_object_or_404(Race, pk=race_id)
    form = RaceCommentForm(request.POST or None, initial={"race_date": race.date})
    if request.method == "POST" and form.is_valid():
        comment = form.save(commit=False)
        comment.race = race
        comment.author = request.user
        comment.save()
        return redirect("race_detail", pk=race.pk)
    return render(request, "races/comment_form.html", {"form": form, "race": race})


@login_required
def my_entries(request):
    entries = RaceEntry.objects.filter(user=request.user).select_related("race")
    return render(request, "races/my_entries.html", {"entries": entries})


@staff_required
def result_create(request, race_id):
    race = get_object_or_404(Race, pk=race_id)
    form = RaceResultForm(request.POST or None, race=race)
    if request.method == "POST" and form.is_valid():
        result = form.save(commit=False)
        result.race = race
        result.save()
        return redirect("race_detail", pk=race.pk)
    return render(request, "races/result_form.html", {"form": form, "race": race, "title": "Добавить результат"})


@staff_required
def result_edit(request, pk):
    result = get_object_or_404(RaceResult, pk=pk)
    form = RaceResultForm(request.POST or None, instance=result, race=result.race)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("race_detail", pk=result.race_id)
    return render(request, "races/result_form.html", {"form": form, "race": result.race, "title": "Изменить результат"})


@staff_required
@require_POST
def result_delete(request, pk):
    result = get_object_or_404(RaceResult, pk=pk)
    race_id = result.race_id
    result.delete()
    return redirect("race_detail", pk=race_id)


@staff_required
def race_create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        location = request.POST.get("location", "").strip()
        date = request.POST.get("date", "").strip()
        if title and location and date:
            Race.objects.create(title=title, description=description, location=location, date=date)
            return redirect("race_list")
    return render(request, "races/race_form.html", {"title": "Новая гонка"})


@staff_required
def race_edit(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if request.method == "POST":
        race.title = request.POST.get("title", "").strip()
        race.description = request.POST.get("description", "").strip()
        race.location = request.POST.get("location", "").strip()
        race.date = request.POST.get("date", "").strip()
        race.save()
        return redirect("race_detail", pk=race.pk)
    return render(request, "races/race_form.html", {"race": race, "title": "Редактировать гонку"})


@staff_required
@require_POST
def race_delete(request, pk):
    race = get_object_or_404(Race, pk=pk)
    race.delete()
    return redirect("race_list")
