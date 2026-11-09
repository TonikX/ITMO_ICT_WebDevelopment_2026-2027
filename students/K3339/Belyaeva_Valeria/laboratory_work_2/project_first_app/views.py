from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from flights.models import User
from .forms import OwnerForm
from .models import Car


@user_passes_test(lambda user: user.is_active and user.is_staff)
def owners(request):
    return render(request, 'practice/owners.html', {'owners': User.objects.filter(is_staff=False).prefetch_related('cars').order_by('last_name', 'first_name')})


@user_passes_test(lambda user: user.is_active and user.is_staff)
def owner_detail(request, pk):
    return render(request, 'practice/owner.html', {'owner': get_object_or_404(User, pk=pk)})


@user_passes_test(lambda user: user.is_active and user.is_staff)
def owner_create(request):
    form = OwnerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        owner = form.save()
        messages.success(request, 'Владелец создан.')
        return redirect('owner_detail', pk=owner.pk)
    return render(request, 'flights/form.html', {'form': form, 'title': 'Новый владелец', 'eyebrow': 'ПРАКТИКА 2.1–2.3',
                  'subtitle': 'Пользователь с дополнительными атрибутами.', 'button': 'Создать владельца'})


class StaffRequired(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff


class CarList(StaffRequired, ListView):
    model = Car
    template_name = 'practice/cars.html'
    context_object_name = 'cars'


class CarDetail(StaffRequired, DetailView):
    model = Car
    template_name = 'practice/car.html'
    context_object_name = 'car'


class CarCreate(StaffRequired, CreateView):
    model = Car
    fields = ['registration_number', 'brand', 'model', 'color']
    template_name = 'flights/form.html'
    success_url = reverse_lazy('car_list')
    extra_context = {'title': 'Новый автомобиль', 'eyebrow': 'ПРАКТИКА 2.2', 'subtitle': 'Создание через CreateView.', 'button': 'Сохранить'}


class CarUpdate(StaffRequired, UpdateView):
    model = Car
    fields = ['registration_number', 'brand', 'model', 'color']
    template_name = 'flights/form.html'
    success_url = reverse_lazy('car_list')
    extra_context = {'title': 'Изменить автомобиль', 'eyebrow': 'ПРАКТИКА 2.2', 'subtitle': 'Редактирование через UpdateView.', 'button': 'Сохранить'}


class CarDelete(StaffRequired, DeleteView):
    model = Car
    template_name = 'practice/delete.html'
    success_url = reverse_lazy('car_list')
