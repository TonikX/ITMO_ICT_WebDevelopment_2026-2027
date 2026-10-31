from django.http import HttpResponse
from .models import CarOwner, Automobile
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CarOwnerForm, UserCreateForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Automobile

class AutomobileListView(ListView):
    model = Automobile
    template_name = 'automobile_list.html'
    context_object_name = 'automobiles'

class AutomobileCreateView(CreateView):
    model = Automobile
    fields = [
        'registration_number',
        'brand',
        'model',
        'color'
    ]
    template_name = 'automobile_form.html'
    success_url = reverse_lazy('automobile_list')


def home(request):
    return HttpResponse(
        "Добро пожаловать! Приложение Django работает."
    )


def owner_detail(request, owner_id):
    owner = get_object_or_404(CarOwner, pk=owner_id)
    return render(request, 'owner.html', {'owner': owner})

def owner_list(request):
    owners = CarOwner.objects.all()
    return render(request, 'owner_list.html', {'owners': owners})



def owner_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)

        if form.is_valid():
            user = form.save()

            CarOwner.objects.create(
                user=user,
                surname=user.last_name,
                name=user.first_name
            )

            return redirect('owner_list')
    else:
        form = UserCreateForm()

    return render(request, 'owner_create.html', {'form': form})