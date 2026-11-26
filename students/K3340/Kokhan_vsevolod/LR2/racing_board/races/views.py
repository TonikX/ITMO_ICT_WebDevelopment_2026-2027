from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.http import require_POST, require_http_methods
from django.db.models import Avg, Q

from .models import (
    Race,
    RaceResult,
    DriverProfile,
    Registration,
    Comment,
)

from .forms import (
    RegistrationForm,
    RaceRegistrationForm,
    CommentForm,
    DriverProfileForm,
    RegistrationEditForm,
)


class RaceListView(ListView):
    model = Race
    template_name = 'races/race_list.html'
    context_object_name = 'races'
    paginate_by = 5

    def get_queryset(self):
        queryset = Race.objects.all()

        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search)
            )

        status = self.request.GET.get('status', '')
        if status == 'open':
            queryset = queryset.filter(is_registration_open=True)
        elif status == 'closed':
            queryset = queryset.filter(is_registration_open=False)

        sort = self.request.GET.get('sort', 'date_asc')
        if sort == 'date_desc':
            queryset = queryset.order_by('-start_date')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by('start_date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_sort'] = self.request.GET.get('sort', 'date_asc')
        return context


def home(request):
    races = Race.objects.order_by('start_date')[:6]
    results = RaceResult.objects.select_related(
        'registration__driver__user',
        'registration__driver__team',
        'registration__driver__car',
        'registration__race',
    ).order_by('position')[:10]

    return render(request, 'races/home.html', {
        'races': races,
        'results': results,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно.')
            return redirect('home')
    else:
        form = RegistrationForm()

    return render(request, 'races/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Вы успешно вошли.')
            return redirect('home')
    else:
        form = AuthenticationForm(request)

    return render(request, 'races/login.html', {'form': form})


@login_required
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('home')


@login_required
def profile(request):
    driver_profile, _ = DriverProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = DriverProfileForm(request.POST, instance=driver_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('profile')
    else:
        form = DriverProfileForm(instance=driver_profile)

    return render(request, 'races/profile.html', {
        'driver_profile': driver_profile,
        'form': form,
    })


@login_required
@require_POST
def register_for_race(request, race_id):
    race = get_object_or_404(Race, id=race_id)

    if not race.is_registration_open:
        messages.error(request, 'Регистрация на эту гонку закрыта.')
        return redirect('race_detail', race_id=race.id)

    driver_profile, _ = DriverProfile.objects.get_or_create(user=request.user)

    if Registration.objects.filter(driver=driver_profile, race=race).exists():
        messages.warning(request, 'Вы уже подали заявку на эту гонку.')
        return redirect('race_detail', race_id=race.id)

    form = RaceRegistrationForm(request.POST)
    if form.is_valid():
        registration = form.save(commit=False)
        registration.driver = driver_profile
        registration.race = race
        registration.save()
        messages.success(request, 'Заявка на участие отправлена.')
    else:
        # Если форма пустая / без comment — всё равно создаём
        Registration.objects.create(driver=driver_profile, race=race)
        messages.success(request, 'Заявка на участие отправлена.')

    return redirect('my_registrations')


@login_required
def my_registrations(request):
    registrations = Registration.objects.filter(
        driver__user=request.user,
    ).select_related(
        'race',
        'driver__team',
        'driver__car',
    ).order_by('-registered_at')

    return render(request, 'races/my_registrations.html', {
        'registrations': registrations,
    })


@login_required
def edit_registration(request, registration_id):
    registration = get_object_or_404(
        Registration,
        id=registration_id,
        driver__user=request.user,
    )

    if registration.status != 'pending':
        messages.error(request, 'Можно редактировать только заявки со статусом «На рассмотрении».')
        return redirect('my_registrations')

    if request.method == 'POST':
        form = RegistrationEditForm(request.POST, instance=registration)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заявка обновлена.')
            return redirect('my_registrations')
    else:
        form = RegistrationEditForm(instance=registration)

    return render(request, 'races/edit_registration.html', {
        'form': form,
        'registration': registration,
    })


@login_required
@require_POST
def delete_registration(request, registration_id):
    registration = get_object_or_404(
        Registration,
        id=registration_id,
        driver__user=request.user,
    )

    # Разрешаем удалять только pending или rejected
    if registration.status == 'approved':
        messages.error(request, 'Нельзя удалить уже подтверждённую заявку. Обратитесь к администратору.')
        return redirect('my_registrations')

    race_name = registration.race.name
    registration.delete()
    messages.success(request, f'Заявка на «{race_name}» удалена.')
    return redirect('my_registrations')


@user_passes_test(lambda user: user.is_staff)
def manage_registrations(request):
    registrations = Registration.objects.select_related(
        'race',
        'driver__user',
        'driver__team',
        'driver__car',
    ).order_by('-registered_at')

    return render(request, 'races/manage_registrations.html', {
        'registrations': registrations,
    })


@user_passes_test(lambda user: user.is_staff)
@require_POST
def update_registration_status(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    status = request.POST.get('status')

    if status not in ('approved', 'rejected', 'pending'):
        messages.error(request, 'Некорректный статус заявки.')
        return redirect('manage_registrations')

    registration.status = status
    registration.save(update_fields=['status'])

    status_labels = {
        'approved': 'подтверждена',
        'rejected': 'отклонена',
        'pending': 'возвращена на рассмотрение',
    }
    messages.success(request, f'Заявка {status_labels.get(status, "обновлена")}.')
    return redirect('manage_registrations')


def race_detail(request, race_id):
    race = get_object_or_404(Race, id=race_id)

    results = RaceResult.objects.filter(
        registration__race=race,
    ).select_related(
        'registration__driver__user',
        'registration__driver__team',
        'registration__driver__car',
    ).order_by('position', 'finish_time')

    # Участники (одобренные заявки) — полное табло
    participants = Registration.objects.filter(
        race=race,
        status='approved',
    ).select_related(
        'driver__user',
        'driver__team',
        'driver__car',
    ).order_by('driver__user__last_name', 'driver__user__first_name')

    comments = Comment.objects.filter(race=race).select_related('author')
    average_rating = comments.aggregate(average=Avg('rating'))['average']

    user_registration = None
    if request.user.is_authenticated:
        try:
            user_registration = Registration.objects.get(
                driver__user=request.user,
                race=race,
            )
        except Registration.DoesNotExist:
            pass

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.race = race
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен.')
            return redirect('race_detail', race_id=race.id)
    else:
        form = CommentForm()

    return render(request, 'races/race_detail.html', {
        'race': race,
        'results': results,
        'participants': participants,
        'comments': comments,
        'average_rating': average_rating,
        'form': form,
        'user_registration': user_registration,
    })
