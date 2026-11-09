from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CarOwner, Car, Ownership
from .forms import CarOwnerForm, CarForm, OwnershipForm
from django.contrib.auth.decorators import login_required
from .models import Racer, Race, RaceRegistration, Review
from .forms import RaceForm, RaceRegistrationForm, ReviewForm
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def car_owner_list(request):
    """Список всех владельцев"""
    owners = CarOwner.objects.all()
    return render(request, 'racing/carowner_list.html', {'owners': owners})


def car_owner_detail(request, pk):
    """Детальная информация о владельце"""
    owner = get_object_or_404(CarOwner, pk=pk)
    return render(request, 'racing/carowner_detail.html', {'owner': owner})


def car_owner_create(request):
    """Создание нового владельца"""
    if request.method == 'POST':
        form = CarOwnerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Владелец успешно создан!')
            return redirect('car_owner_list')
    else:
        form = CarOwnerForm()
    return render(request, 'racing/carowner_form.html', {'form': form, 'title': 'Добавить владельца'})


def car_owner_update(request, pk):
    """Редактирование владельца"""
    owner = get_object_or_404(CarOwner, pk=pk)
    if request.method == 'POST':
        form = CarOwnerForm(request.POST, instance=owner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Владелец успешно обновлён!')
            return redirect('car_owner_detail', pk=pk)
    else:
        form = CarOwnerForm(instance=owner)
    return render(request, 'racing/carowner_form.html', {'form': form, 'title': 'Редактировать владельца'})


def car_owner_delete(request, pk):
    """Удаление владельца"""
    owner = get_object_or_404(CarOwner, pk=pk)
    if request.method == 'POST':
        owner.delete()
        messages.success(request, 'Владелец успешно удалён!')
        return redirect('car_owner_list')
    return render(request, 'racing/confirm_delete.html', {'object': owner, 'type': 'владелец'})


def car_list(request):
    """Список всех автомобилей"""
    cars = Car.objects.all()
    return render(request, 'racing/car_list.html', {'cars': cars})


def car_detail(request, pk):
    """Детальная информация об автомобиле"""
    car = get_object_or_404(Car, pk=pk)
    return render(request, 'racing/car_detail.html', {'car': car})


def car_create(request):
    """Создание нового автомобиля"""
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Автомобиль успешно создан!')
            return redirect('car_list')
    else:
        form = CarForm()
    return render(request, 'racing/car_form.html', {'form': form, 'title': 'Добавить автомобиль'})


def car_update(request, pk):
    """Редактирование автомобиля"""
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, 'Автомобиль успешно обновлён!')
            return redirect('car_detail', pk=pk)
    else:
        form = CarForm(instance=car)
    return render(request, 'racing/car_form.html', {'form': form, 'title': 'Редактировать автомобиль'})


def car_delete(request, pk):
    """Удаление автомобиля"""
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Автомобиль успешно удалён!')
        return redirect('car_list')
    return render(request, 'racing/confirm_delete.html', {'object': car, 'type': 'автомобиль'})


def race_list(request):
    """Список всех гонок"""
    races = Race.objects.all()
    return render(request, 'racing/race_list.html', {'races': races})


def race_detail(request, pk):
    """Детальная информация о гонке с таблицей результатов и отзывами"""
    race = get_object_or_404(Race, pk=pk)
    registrations = race.registrations.select_related('racer').all()
    reviews = race.reviews.select_related('author').all()

    user_registered = False
    user_registration = None
    if request.user.is_authenticated:
        try:
            racer = request.user.racer_profile
            user_registration = RaceRegistration.objects.filter(race=race, racer=racer).first()
            user_registered = user_registration is not None
        except Racer.DoesNotExist:
            pass

    review_form = ReviewForm() if request.user.is_authenticated else None

    context = {
        'race': race,
        'registrations': registrations,
        'reviews': reviews,
        'user_registered': user_registered,
        'user_registration': user_registration,
        'review_form': review_form,
    }
    return render(request, 'racing/race_detail.html', context)


@login_required
def race_register(request, pk):
    """Регистрация текущего пользователя на гонку"""
    race = get_object_or_404(Race, pk=pk)

    racer, created = Racer.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': request.user.first_name or request.user.username,
            'last_name': request.user.last_name or 'Гонщик',
            'team_name': 'Команда по умолчанию',
            'car_description': 'Описание автомобиля',
            'experience': 0,
            'racer_class': 'Новичок',
        }
    )

    if request.method == 'POST':
        registration, reg_created = RaceRegistration.objects.get_or_create(racer=racer, race=race)
        if reg_created:
            messages.success(request, f'Вы успешно зарегистрированы на гонку "{race.name}"!')
        else:
            messages.info(request, 'Вы уже зарегистрированы на эту гонку.')
        return redirect('race_detail', pk=pk)

    return render(request, 'racing/race_register_confirm.html', {'race': race, 'racer': racer})


@login_required
def race_unregister(request, pk):
    """Удаление регистрации текущего пользователя с гонки"""
    race = get_object_or_404(Race, pk=pk)

    if request.method == 'POST':
        try:
            racer = request.user.racer_profile
            registration = RaceRegistration.objects.get(racer=racer, race=race)
            registration.delete()
            messages.success(request, f'Ваша регистрация на гонку "{race.name}" удалена.')
        except (Racer.DoesNotExist, RaceRegistration.DoesNotExist):
            messages.error(request, 'Вы не зарегистрированы на эту гонку.')
        return redirect('race_detail', pk=pk)

    return render(request, 'racing/race_unregister_confirm.html', {'race': race})


@login_required
def review_create(request, pk):
    """Создание отзыва к гонке"""
    race = get_object_or_404(Race, pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.race = race
            review.author = request.user
            review.save()
            messages.success(request, 'Ваш отзыв добавлен!')
            return redirect('race_detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'racing/review_form.html', {'form': form, 'race': race})


@login_required
def review_delete(request, pk):
    """Удаление своего отзыва"""
    review = get_object_or_404(Review, pk=pk)

    if review.author != request.user:
        messages.error(request, 'Вы не можете удалить чужой отзыв.')
        return redirect('race_detail', pk=review.race.pk)

    if request.method == 'POST':
        race_pk = review.race.pk
        review.delete()
        messages.success(request, 'Ваш отзыв удалён.')
        return redirect('race_detail', pk=race_pk)

    return render(request, 'racing/review_delete_confirm.html', {'review': review})


def race_results(request, pk):
    """Таблица результатов конкретной гонки"""
    race = get_object_or_404(Race, pk=pk)
    registrations = race.registrations.select_related('racer', 'racer__user').all()

    context = {
        'race': race,
        'registrations': registrations,
    }
    return render(request, 'racing/race_results.html', context)


def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('race_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'racing/register.html', {'form': form})


def login_view(request):
    """Вход в систему"""
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Вы вошли в систему!')
            redirect_to = next_url if next_url and next_url != 'None' else 'race_list'
            return redirect(redirect_to)
    else:
        form = CustomAuthenticationForm()
    return render(request, 'racing/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('race_list')
