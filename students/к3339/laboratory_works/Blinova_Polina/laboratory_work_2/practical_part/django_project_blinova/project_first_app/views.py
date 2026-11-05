from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView,
    CreateView, UpdateView, DeleteView,
)

from .models import Car
from .forms import UserRegisterForm, CarForm

User = get_user_model()



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_detail', user_id=user.id)
    else:
        form = UserRegisterForm()

    return render(request, 'project_first_app/register.html', {
        'form': form,
        'title': 'Регистрация',
    })


def user_list(request):
    users = User.objects.filter(is_staff=False)
    return render(request, 'project_first_app/user_list.html', {
        'users': users,
    })


def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    licenses = user.licenses.all()
    ownerships = user.ownerships.select_related('car').all()

    return render(request, 'project_first_app/user.html', {
        'owner': user,
        'licenses': licenses,
        'ownerships': ownerships,
    })



class CarListView(ListView):
    model = Car
    template_name = 'project_first_app/car_list.html'
    context_object_name = 'cars'
    paginate_by = 10


class CarDetailView(DetailView):
    model = Car
    template_name = 'project_first_app/car_detail.html'
    context_object_name = 'car'


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