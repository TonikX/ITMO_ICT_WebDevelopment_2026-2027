from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from accounts.forms import OwnerRegistrationForm
from flights.views import require_staff
from .forms import CarForm
from .models import Car


@login_required
def owner_list(request):
    require_staff(request.user)
    owners = get_user_model().objects.filter(is_staff=False).prefetch_related('cars').order_by('last_name', 'username')
    return render(request, 'practice/owners.html', {'owners': owners})


@login_required
def owner_detail(request, pk):
    require_staff(request.user)
    owner = get_object_or_404(get_user_model(), pk=pk)
    return render(request, 'practice/owner.html', {'owner': owner,
        'ownerships': owner.ownership_set.select_related('car').order_by('start_date')})


@login_required
def owner_create(request):
    require_staff(request.user)
    form = OwnerRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        owner = form.save()
        messages.success(request, 'Автовладелец создан.')
        return redirect('owner', pk=owner.pk)
    return render(request, 'form.html', {'form': form, 'title': 'Создать автовладельца',
        'submit': 'Создать пользователя', 'back_url': '/practice/owners/'})


class StaffMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class CarList(StaffMixin, ListView):
    model = Car
    template_name = 'practice/cars.html'


class CarDetail(StaffMixin, DetailView):
    model = Car
    template_name = 'practice/car.html'


class CarCreate(StaffMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = 'form.html'
    success_url = reverse_lazy('cars')
    extra_context = {'title': 'Создать автомобиль', 'submit': 'Сохранить', 'back_url': '/practice/cars/'}


class CarUpdate(StaffMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'form.html'
    success_url = reverse_lazy('cars')
    extra_context = {'title': 'Изменить автомобиль', 'submit': 'Сохранить', 'back_url': '/practice/cars/'}


class CarDelete(StaffMixin, DeleteView):
    model = Car
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('cars')
    extra_context = {'back_url': '/practice/cars/'}
