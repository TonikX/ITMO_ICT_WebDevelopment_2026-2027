from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import CarOwnerForm

def owner_by_id(request, owner_id):
    from .models import CarOwner
    owner = CarOwner.objects.get(id=owner_id)
    return render(request, 'owner.html', {'owner': owner})

def list_owners(request):
    from .models import CarOwner
    owners = CarOwner.objects.all()
    return render(request, 'owners_list.html', {'owners': owners})

class CarListView(ListView):
    from .models import Car
    model = Car
    template_name = 'car_list.html'
    context_object_name = 'cars'

class CarDetailView(DetailView):
    from .models import Car
    model = Car
    template_name = 'car_detail.html'
    context_object_name = 'car'

def create_car_owner(request):
    if request.method == 'POST':
        form = CarOwnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_owners)
    else:
        form = CarOwnerForm()
    return render(request, 'create_owner.html', {'form': form})

class CarCreateView(CreateView):
    from .models import Car
    model = Car
    fields = ['brand', 'model', 'color', 'gov_number']
    template_name = 'car_form.html'
    success_url = '/cars/'

class CarUpdateView(UpdateView):
    from .models import Car
    model = Car
    fields = ['brand', 'model', 'color', 'gov_number']
    template_name = 'car_form.html'
    success_url = '/cars/'

class CarDeleteView(DeleteView):
    from .models import Car
    model = Car
    template_name = 'car_confirm_delete.html'
    success_url = '/cars/'