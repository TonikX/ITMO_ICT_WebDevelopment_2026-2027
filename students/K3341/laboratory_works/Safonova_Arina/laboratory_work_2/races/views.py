from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import CommentForm, RegistrationForm, ResultForm
from .models import Race, Registration, Comment


def race_list(request):
    query = request.GET.get('q', '').strip()
    races = Race.objects.filter(name__icontains=query)
    page = Paginator(races, 5).get_page(request.GET.get('page'))
    return render(request, 'race_list.html', {'page': page, 'query': query})


def race_detail(request, pk):
    race = get_object_or_404(Race, pk=pk)
    entries = Registration.objects.filter(race=race)
    comments = Comment.objects.filter(race=race).select_related('user')
    return render(request, 'race_detail.html', {'race': race, 'entries': entries, 'comments': comments})


def register(request):
    form = UserCreationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())
        return redirect('race_list')
    return render(request, 'form.html', {'form': form, 'title': 'Регистрация пользователя'})


def sign_in(request):
    form = AuthenticationForm(request, data=request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('race_list')
    return render(request, 'form.html', {'form': form, 'title': 'Вход'})


@require_POST
def sign_out(request):
    logout(request)
    return redirect('race_list')


@login_required
def my_registrations(request):
    entries = Registration.objects.filter(user=request.user).select_related('race')
    return render(request, 'my_registrations.html', {'entries': entries})


@login_required
def registration_create(request, pk):
    race = get_object_or_404(Race, pk=pk)
    form = RegistrationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        entry = form.save(commit=False)
        entry.user = request.user
        entry.race = race
        entry.save()
        return redirect('my_registrations')
    return render(request, 'form.html', {'form': form, 'title': 'Регистрация гонщика'})


@login_required
def registration_edit(request, pk):
    entry = get_object_or_404(Registration, pk=pk, user=request.user)
    form = RegistrationForm(request.POST if request.method == 'POST' else None, instance=entry)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('my_registrations')
    return render(request, 'form.html', {'form': form, 'title': 'Изменение регистрации'})


@login_required
def registration_delete(request, pk):
    entry = get_object_or_404(Registration, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        return redirect('my_registrations')
    return render(request, 'delete.html', {'entry': entry})


@login_required
def comment_create(request, pk):
    race = get_object_or_404(Race, pk=pk)
    form = CommentForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.race = race
        comment.user = request.user
        comment.start_date = race.start_date
        comment.end_date = race.end_date
        comment.save()
        return redirect('race_detail', pk=race.pk)
    return render(request, 'form.html', {'form': form, 'title': f'Комментарий: {race.name}'})


@login_required
def result_edit(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied
    entry = get_object_or_404(Registration, pk=pk)
    form = ResultForm(request.POST if request.method == 'POST' else None, instance=entry)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('race_detail', pk=entry.race_id)
    return render(request, 'form.html', {'form': form, 'title': f'Результат: {entry.full_name}'})
