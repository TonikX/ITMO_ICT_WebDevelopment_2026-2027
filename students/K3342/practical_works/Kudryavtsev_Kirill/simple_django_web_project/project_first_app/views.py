from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .forms import OwnerForm
from .models import Car, CarOwner


def owner_list(request):
    return render(request, 'owners.html', {'owners': CarOwner.objects.filter(is_superuser=False)})


def owner_detail(request, pk):
    owner = get_object_or_404(CarOwner, pk=pk)
    return render(request, 'owner.html', {'owner': owner, 'ownerships': owner.ownership_set.select_related('car'), 'licenses': owner.licenses.all()})


def registration(request):
    form = OwnerForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('owner_detail', pk=user.pk)
    return render(request, 'form.html', {'form': form, 'title': 'Регистрация автовладельца'})


@login_required
def owner_create(request):
    if not request.user.is_staff:
        raise PermissionDenied
    form = OwnerForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        owner = form.save()
        return redirect('owner_detail', pk=owner.pk)
    return render(request, 'form.html', {'form': form, 'title': 'Добавить владельца'})


class StaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class CarList(ListView):
    model = Car
    template_name = 'cars.html'
    context_object_name = 'cars'


class CarDetail(DetailView):
    model = Car
    template_name = 'car.html'


class CarCreate(StaffMixin, CreateView):
    model = Car
    fields = ['plate', 'brand', 'model', 'color']
    template_name = 'form.html'
    extra_context = {'title': 'Добавить автомобиль'}
    success_url = reverse_lazy('car_list')


class CarUpdate(StaffMixin, UpdateView):
    model = Car
    fields = ['plate', 'brand', 'model', 'color']
    template_name = 'form.html'
    extra_context = {'title': 'Изменить автомобиль'}
    success_url = reverse_lazy('car_list')


class CarDelete(StaffMixin, DeleteView):
    model = Car
    template_name = 'delete.html'
    success_url = reverse_lazy('car_list')
