from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .models import Race, Registration
from .forms import RegisterForm, RegistrationForm, CommentForm, RaceForm, ResultForm


def race_list(request):
    races = Race.objects.all()

    search_query = request.GET.get('search', '').strip()
    if search_query:
        races = races.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    year = request.GET.get('year', '').strip()
    if year and year.isdigit():
        races = races.filter(date__year=int(year))

    paginator = Paginator(races, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    years = Race.objects.dates('date', 'year', order='DESC')
    years = [d.year for d in years]

    return render(request, 'race_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'year': year,
        'years': years,
    })

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('race_list')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('race_list')

def race_detail(request, pk):
    race = get_object_or_404(Race, pk=pk)
    registrations = race.registrations.all()
    comments = race.comments.all()
    return render(request, 'race_detail.html', {
        'race': race,
        'registrations': registrations,
        'comments': comments,
    })

@login_required
def registration_create(request, race_id):
    race = get_object_or_404(Race, pk=race_id)

    if Registration.objects.filter(user=request.user, race=race).exists():
        messages.warning(request, 'Вы уже зарегистрированы на эту гонку')
        return redirect('race_detail', pk=race_id)

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.race = race
            registration.save()
            messages.success(request, 'Вы успешно зарегистрированы на гонку')
            return redirect('race_detail', pk=race_id)
    else:
        form = RegistrationForm()

    return render(request, 'registration_create.html', {'form': form, 'race': race})

@login_required
def my_registrations(request):
    registrations = Registration.objects.filter(user=request.user).select_related('race')
    return render(request, 'my_registrations.html', {'registrations': registrations})


@login_required
def registration_edit(request, pk):
    registration = get_object_or_404(Registration, pk=pk, user=request.user)

    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=registration)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация обновлена')
            return redirect('my_registrations')
    else:
        form = RegistrationForm(instance=registration)

    return render(request, 'registration_edit.html', {'form': form, 'registration': registration})


@login_required
def registration_delete(request, pk):
    registration = get_object_or_404(Registration, pk=pk, user=request.user)

    if request.method == 'POST':
        registration.delete()
        messages.success(request, 'Регистрация удалена')
        return redirect('my_registrations')

    return render(request, 'registration_delete.html', {'registration': registration})

@login_required
def comment_create(request, race_id):
    race = get_object_or_404(Race, pk=race_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.race = race
            comment.save()
            messages.success(request, 'Комментарий добавлен')
            return redirect('race_detail', pk=race_id)
    else:
        form = CommentForm()

    return render(request, 'comment_create.html', {'form': form, 'race': race})

@user_passes_test(lambda u: u.is_staff)
def race_create(request):
    if request.method == 'POST':
        form = RaceForm(request.POST)
        if form.is_valid():
            race = form.save()
            messages.success(request, f'Гонка «{race.name}» создана')
            return redirect('race_detail', pk=race.id)
    else:
        form = RaceForm()
    return render(request, 'race_form.html', {'form': form, 'title': 'Создать гонку'})


@user_passes_test(lambda u: u.is_staff)
def race_edit(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if request.method == 'POST':
        form = RaceForm(request.POST, instance=race)
        if form.is_valid():
            form.save()
            messages.success(request, 'Гонка обновлена')
            return redirect('race_detail', pk=race.id)
    else:
        form = RaceForm(instance=race)
    return render(request, 'race_form.html', {'form': form, 'title': 'Редактировать гонку'})


@user_passes_test(lambda u: u.is_staff)
def race_delete(request, pk):
    race = get_object_or_404(Race, pk=pk)
    if request.method == 'POST':
        race.delete()
        messages.success(request, 'Гонка удалена')
        return redirect('race_list')
    return render(request, 'race_delete.html', {'race': race})


@user_passes_test(lambda u: u.is_staff)
def registration_set_result(request, pk):
    registration = get_object_or_404(Registration, pk=pk)
    if request.method == 'POST':
        form = ResultForm(request.POST, instance=registration)
        if form.is_valid():
            form.save()
            messages.success(request, 'Результат сохранён')
            return redirect('race_detail', pk=registration.race.id)
    else:
        form = ResultForm(instance=registration)
    return render(request, 'result_form.html', {
        'form': form,
        'registration': registration,
    })

