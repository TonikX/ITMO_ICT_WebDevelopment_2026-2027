from functools import wraps
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, Q, F
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import SignupForm, DriverForm, EntryForm, CommentForm, HeatForm
from .models import Driver, Race, Entry, Heat


def page(request, template, **context):
    def query_url(**changes):
        query = request.GET.copy()
        for key, value in changes.items():
            if value in ('', None):
                query.pop(key, None)
            else:
                query[key] = value
        return '?' + query.urlencode()
    context.update(query_url=query_url, classes=Driver.CLASSES)
    return render(request, 'racing/' + template + '.html', context)


def home(request):
    upcoming = Race.objects.annotate(entry_count=Count('entries')).filter(status='open', start_date__gte=timezone.localdate()).order_by('start_date', 'pk')[:3]
    latest = Race.objects.filter(status='finished').order_by('-end_date', '-pk').first()
    leaders = Heat.objects.select_related('entry__driver').filter(entry__race=latest, attempt=1, status='finished').order_by('position')[:5] if latest else []
    return page(request, 'home', upcoming=upcoming, latest=latest, leaders=leaders,
                race_count=Race.objects.count(), driver_count=Driver.objects.count())


def race_list(request):
    races = Race.objects.annotate(entry_count=Count('entries', distinct=True)).order_by('start_date', 'pk')
    q, status = request.GET.get('q', '').strip(), request.GET.get('status', '')
    if q:
        races = races.filter(Q(title__icontains=q) | Q(track__icontains=q) | Q(location__icontains=q))
    if status in dict(Race.STATUSES):
        races = races.filter(status=status)
    return page(request, 'races', races=Paginator(races, 6).get_page(request.GET.get('page')), q=q, status=status, statuses=Race.STATUSES)


def race_detail(request, slug):
    race = get_object_or_404(Race, slug=slug)
    heats = Heat.objects.filter(entry__race=race).select_related('entry__driver').order_by('attempt', F('position').asc(nulls_last=True), 'pk')
    q, category = request.GET.get('q', '').strip(), request.GET.get('class', '')
    if q:
        heats = heats.filter(Q(entry__driver__full_name__icontains=q) | Q(entry__driver__team__icontains=q) | Q(entry__driver__car__icontains=q))
    if category in dict(Driver.CLASSES):
        heats = heats.filter(entry__driver__racing_class=category)
    own_entry = race.entries.filter(driver__user=request.user).first() if request.user.is_authenticated else None
    return page(request, 'detail', race=race, q=q, category=category,
                heats=Paginator(heats, 10).get_page(request.GET.get('page')),
                entries=race.entries.select_related('driver'), own_entry=own_entry,
                comments=Paginator(race.comments.select_related('author'), 5).get_page(request.GET.get('cp')),
                comment_form=CommentForm(initial={'date_from': race.start_date, 'date_to': race.end_date}),
                entry_count=race.entries.count())


def drivers(request):
    objects = Driver.objects.annotate(starts=Count('entries', distinct=True)).order_by('full_name', 'pk')
    q, category = request.GET.get('q', '').strip(), request.GET.get('class', '')
    if q:
        objects = objects.filter(Q(full_name__icontains=q) | Q(team__icontains=q) | Q(car__icontains=q))
    if category in dict(Driver.CLASSES):
        objects = objects.filter(racing_class=category)
    return page(request, 'drivers', drivers=Paginator(objects, 9).get_page(request.GET.get('page')), q=q, category=category)


def signup(request):
    if request.user.is_authenticated:
        return redirect('my_entries')
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Аккаунт создан. Выберите гонку и заполните заявку.')
        return redirect('races')
    return page(request, 'auth', form=form, signup=True)


@require_POST
def signout(request):
    logout(request)
    return redirect('home')


@login_required
def my_entries(request):
    entries = Entry.objects.filter(driver__user=request.user).select_related('race', 'driver').annotate(result_count=Count('heats'))
    return page(request, 'my_entries', entries=entries)


@login_required
def entry_edit(request, slug, pk=None):
    race = get_object_or_404(Race, slug=slug)
    entry = get_object_or_404(Entry, pk=pk, race=race, driver__user=request.user) if pk else None
    if not race.accepts_entries or (entry and entry.heats.exists()):
        raise PermissionDenied('Приём и изменение заявок закрыты.')
    if not entry and Entry.objects.filter(race=race, driver__user=request.user).exists():
        messages.info(request, 'Вы уже зарегистрированы на эту гонку.')
        return redirect('my_entries')
    driver = Driver.objects.filter(user=request.user).first()
    profile_form = DriverForm(request.POST or None, instance=driver,
                              initial={'full_name': request.user.first_name} if driver is None else {})
    form = EntryForm(request.POST or None, race=race, instance=entry)
    if request.method == 'POST':
        valid_profile, valid_entry = profile_form.is_valid(), form.is_valid()
        if valid_profile and valid_entry:
            try:
                with transaction.atomic():
                    locked_race = Race.objects.select_for_update().get(pk=race.pk)
                    if not locked_race.accepts_entries:
                        raise PermissionDenied('Регистрация закрыта.')
                    if not entry and locked_race.entries.count() >= locked_race.capacity:
                        form.add_error(None, 'Все места заняты. Выберите другую гонку.')
                    elif entry and Entry.objects.get(pk=entry.pk).heats.exists():
                        raise PermissionDenied('У заявки уже есть результаты.')
                    else:
                        profile = profile_form.save(commit=False)
                        profile.user = request.user
                        profile.save()
                        saved = form.save(commit=False)
                        saved.driver, saved.race = profile, locked_race
                        saved.save()
                        messages.success(request, 'Заявка обновлена.' if entry else 'Вы в стартовом списке. До встречи на трассе!')
                        return redirect('my_entries')
            except IntegrityError:
                form.add_error(None, 'Номер или регистрация уже заняты. Обновите страницу и попробуйте снова.')
    return page(request, 'entry_form', race=race, form=form, profile_form=profile_form, entry=entry)


@login_required
def entry_delete(request, pk):
    entry = get_object_or_404(Entry.objects.select_related('race', 'driver'), pk=pk, driver__user=request.user)
    if request.method == 'POST':
        with transaction.atomic():
            race = Race.objects.select_for_update().get(pk=entry.race_id)
            if not race.accepts_entries or entry.heats.exists():
                raise PermissionDenied('Нельзя отменить заявку после закрытия регистрации или появления результатов.')
            entry.delete()
        messages.success(request, 'Заявка отменена.')
        return redirect('my_entries')
    return page(request, 'delete', entry=entry)


@login_required
@require_POST
def comment_add(request, slug):
    race = get_object_or_404(Race, slug=slug)
    form = CommentForm(request.POST)
    form.instance.race, form.instance.author = race, request.user
    if form.is_valid():
        form.save()
        messages.success(request, 'Комментарий опубликован.')
        return redirect(reverse('race_detail', args=[slug]) + '#discussion')
    return page(request, 'comment_form', race=race, form=form)


def staff_only(view):
    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied('Доступ только для судей.')
        return view(request, *args, **kwargs)
    return wrapped


@staff_only
def race_control(request):
    return page(request, 'control', races=Race.objects.annotate(entry_count=Count('entries', distinct=True), heat_count=Count('entries__heats', distinct=True)).order_by('start_date', 'pk'))


@staff_only
def heat_edit(request, slug, pk=None):
    race = get_object_or_404(Race, slug=slug)
    heat = get_object_or_404(Heat, pk=pk, entry__race=race) if pk else None
    form = HeatForm(request.POST or None, instance=heat, race=race,
                    initial={'started_at': f'{race.start_date.isoformat()}T12:00'})
    if request.method == 'POST':
        with transaction.atomic():
            Race.objects.select_for_update().get(pk=race.pk)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        form.save()
                    messages.success(request, 'Результат заезда сохранён.')
                    return redirect(reverse('race_detail', args=[slug]) + '#results')
                except IntegrityError:
                    form.add_error(None, 'Этот заезд уже записан. Обновите страницу.')
    return page(request, 'heat_form', race=race, form=form, heat=heat)
