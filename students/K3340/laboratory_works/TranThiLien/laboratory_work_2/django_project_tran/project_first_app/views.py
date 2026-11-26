from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CarForm, CarOwnerForm
from .models import Car, CarOwner


# ---------------- Практика 2.1 ----------------

def owner_detail(request, owner_id):
    """Информация о владельце автомобиля по его идентификатору."""
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, 'owner.html', {'owner': owner})


# ---------------- Практика 2.2: FBV для владельцев ----------------

def owner_list(request):
    """Вывод всех владельцев (функционально)."""
    context = {'owners': CarOwner.objects.filter(is_superuser=False).order_by('last_name')}
    return render(request, 'owner_list.html', context)


def owner_create(request):
    """Форма ввода владельца (функционально). В 2.3 — создание пользователя."""
    if request.method == 'POST':
        form = CarOwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('owner_list')
    else:
        form = CarOwnerForm()
    return render(request, 'owner_form.html', {'form': form})


# ---------------- Практика 2.2: CBV для автомобилей ----------------

class CarListView(ListView):
    model = Car
    template_name = 'project_first_app/car_list.html'


class CarDetailView(DetailView):
    model = Car
    template_name = 'project_first_app/car_detail.html'


class CarCreateView(CreateView):
    model = Car
    form_class = CarForm
    template_name = 'project_first_app/car_form.html'
    success_url = reverse_lazy('car_list')


class CarUpdateView(UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'project_first_app/car_form.html'
    success_url = reverse_lazy('car_list')


class CarDeleteView(DeleteView):
    model = Car
    template_name = 'project_first_app/car_confirm_delete.html'
    success_url = reverse_lazy('car_list')
