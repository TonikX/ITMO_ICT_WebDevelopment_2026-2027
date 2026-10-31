"""Представления приложения "Автовладельцы" (Практическое занятие 2).

Задание 2: вывод всех владельцев — функционально (FBV);
вывод автомобилей, одного автомобиля и обновление — на классах (CBV).
Задание 3: форма ввода владельца — функционально (FBV);
создание/обновление/удаление автомобиля — на классах (CBV).
"""

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import OwnerForm
from .models import Car, Owner


# --- Задание 2: FBV -------------------------------------------------------

def get_all_owners(request):
    """Все владельцы (функциональный вид). Шаблон owners.html."""
    dataset = Owner.objects.all()
    return render(request, 'owners.html', {'dataset': dataset})


def owner(request, pk):
    """Страница владельца (из практики 1): /owner/<id>/ -> owner.html."""
    owner_obj = get_object_or_404(Owner, pk=pk)
    context = {
        'owner': owner_obj,
        'ownerships': owner_obj.ownerships.select_related('car'),
    }
    return render(request, 'owner.html', context)


# --- Задание 2: CBV (автомобили) -----------------------------------------

class CarListView(ListView):
    """Все автомобили: object_list в car_list.html."""

    model = Car
    template_name = 'car_list.html'
    ordering = ('brand', 'model')


class CarDetailView(DetailView):
    """Один автомобиль: object в car_detail.html."""

    model = Car
    template_name = 'car_detail.html'


class CarUpdateView(UpdateView):
    """Обновление автомобиля: форма в car_form.html."""

    model = Car
    template_name = 'car_form.html'
    fields = ['brand', 'model', 'color', 'state_number']
    success_url = reverse_lazy('car_list')


# --- Задание 3: FBV — форма владельца ------------------------------------

def create_owner(request):
    """Создание владельца через форму (ModelForm). GET — форма, POST — сохранение."""
    if request.method == 'POST':
        form = OwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('owners_list')
    else:
        form = OwnerForm()
    return render(request, 'create_owner.html', {'form': form})


# --- Задание 3: CBV — создание/обновление/удаление автомобиля -----------

class CarCreateView(CreateView):
    """Создание автомобиля: форма в car_form.html."""

    model = Car
    template_name = 'car_form.html'
    fields = ['brand', 'model', 'color', 'state_number']
    success_url = reverse_lazy('car_list')


class CarDeleteView(DeleteView):
    """Удаление автомобиля: подтверждение в car_confirm_delete.html."""

    model = Car
    template_name = 'car_confirm_delete.html'
    success_url = reverse_lazy('car_list')
