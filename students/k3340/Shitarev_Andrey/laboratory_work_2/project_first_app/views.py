from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import SignupForm, DriverForm, RaceForm, RegistrationForm, CommentForm
from .models import Driver, Race, Registration, Run


def page(request, name, context=None, status=200):
    return render(request, name, context or {}, using='jinja2', status=status)


def show_form(request, form, title, status=200):
    return page(request, 'form.html', {'form': form, 'title': title}, status)


def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())
        return redirect('race_list')
    return show_form(request, form, 'Регистрация', 400 if request.method == 'POST' else 200)


def sign_in(request):
    error = ''
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            return redirect('race_list')
        error = 'Неверное имя пользователя или пароль'
    return page(request, 'login.html', {'error': error}, 400 if error else 200)


@login_required
@require_POST
def sign_out(request):
    logout(request)
    return redirect('race_list')


def race_list(request):
    query = request.GET.get('q', '').strip()
    place = request.GET.get('place', '').strip()
    races = Race.objects.order_by('date', 'id')
    if query:
        races = races.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if place:
        races = races.filter(place__icontains=place)
    pages = Paginator(races, 3)
    return page(request, 'race_list.html', {'races': pages.get_page(request.GET.get('page')), 'query': query, 'place': place})


def race_detail(request, race_id):
    race = get_object_or_404(Race, pk=race_id)
    runs = Run.objects.filter(registration__race=race).select_related('registration__driver').order_by('place', 'id')
    registered = request.user.is_authenticated and Registration.objects.filter(driver__user=request.user, race=race).exists()
    return page(request, 'race_detail.html', {'race': race, 'runs': runs, 'comments': race.comments.select_related('author'), 'comment_form': CommentForm(), 'registered': registered})


@login_required
def driver_profile(request):
    driver = Driver.objects.filter(user=request.user).first()
    form = DriverForm(request.POST or None, instance=driver)
    if request.method == 'POST' and form.is_valid():
        driver = form.save(commit=False)
        driver.user = request.user
        driver.save()
        return redirect('race_list')
    return show_form(request, form, 'Профиль гонщика', 400 if request.method == 'POST' else 200)


@login_required
def registration_create(request, race_id):
    race = get_object_or_404(Race, pk=race_id)
    driver = Driver.objects.filter(user=request.user).first()
    if not driver:
        return redirect('profile')
    if Registration.objects.filter(driver=driver, race=race).exists():
        return HttpResponseBadRequest('Вы уже зарегистрированы на гонку')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        registration = form.save(commit=False)
        registration.driver, registration.race = driver, race
        try:
            with transaction.atomic():
                registration.save()
        except IntegrityError:
            return HttpResponseBadRequest('Вы уже зарегистрированы на гонку')
        return redirect('race_detail', race_id=race.pk)
    return show_form(request, form, 'Регистрация на гонку', 400 if request.method == 'POST' else 200)


@login_required
def my_registrations(request):
    registrations = Registration.objects.filter(driver__user=request.user).select_related('race')
    return page(request, 'registrations.html', {'registrations': registrations})


@login_required
def registration_edit(request, pk):
    registration = get_object_or_404(Registration, pk=pk, driver__user=request.user)
    form = RegistrationForm(request.POST or None, instance=registration)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('my_registrations')
    return show_form(request, form, 'Изменение регистрации', 400 if request.method == 'POST' else 200)


@login_required
@require_POST
def registration_delete(request, pk):
    registration = get_object_or_404(Registration, pk=pk, driver__user=request.user)
    registration.delete()
    return redirect('my_registrations')


@login_required
@require_POST
def comment_create(request, race_id):
    race = get_object_or_404(Race, pk=race_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.race, comment.author = race, request.user
        comment.save()
        return redirect('race_detail', race_id=race.pk)
    return show_form(request, form, 'Комментарий', 400)


@user_passes_test(lambda user: user.is_staff)
def race_edit(request, race_id=None):
    race = get_object_or_404(Race, pk=race_id) if race_id else None
    form = RaceForm(request.POST or None, instance=race)
    if request.method == 'POST' and form.is_valid():
        race = form.save()
        return redirect('race_detail', race_id=race.pk)
    return show_form(request, form, 'Гонка', 400 if request.method == 'POST' else 200)


@user_passes_test(lambda user: user.is_staff)
@require_POST
def race_delete(request, race_id):
    race = get_object_or_404(Race, pk=race_id)
    race.delete()
    return redirect('race_list')
