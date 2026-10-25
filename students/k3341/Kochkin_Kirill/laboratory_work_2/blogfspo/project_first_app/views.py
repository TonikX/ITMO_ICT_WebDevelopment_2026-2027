from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Car
from .forms import UserCreateForm
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth import get_user_model

User = get_user_model()

def owner_detail(request, owner_id):
    owner = get_object_or_404(User, pk=owner_id)
    return render(request, 'owner.html', {'owner': owner})

def owner_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('owner_list')
    else:
        form = UserCreateForm()

    return render(request, 'owner_create.html', {'form': form})

def owner_list(request):
    context = {}
    context['dataset'] = User.objects.all()

    return render(
        request,
        'owner_list.html',
        context
    )

class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'


class CarDetailView(DetailView):
    model = Car
    template_name = 'car_detail.html'


class CarUpdateView(UpdateView):
    model = Car
    fields = ['state_number', 'brand', 'model', 'color']
    template_name = 'car_update.html'
    success_url = '/cars/'

class CarCreateView(CreateView):
    model = Car
    fields = ['state_number', 'brand', 'model', 'color']
    template_name = 'car_create.html'
    success_url = '/cars/'

class CarDeleteView(DeleteView):
    model = Car
    template_name = 'car_delete.html'
    success_url = '/cars/'