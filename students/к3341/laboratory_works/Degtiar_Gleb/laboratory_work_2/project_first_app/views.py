from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from accounts.forms import RegistrationForm
from tours.views import StaffMixin,is_staff,paginate
from .models import Car
from .forms import CarForm

@login_required
def owners(request):
    if not is_staff(request.user): raise PermissionDenied
    qs=get_user_model().objects.all().order_by('username')
    q=request.GET.get('q','')[:150]
    if q: qs=qs.filter(username__icontains=q)
    return render(request,'practice/owners.html',{'page_obj':paginate(request,qs),'q':q})

@login_required
def owner_detail(request,pk):
    if not is_staff(request.user): raise PermissionDenied
    owner=get_object_or_404(get_user_model(),pk=pk)
    return render(request,'practice/owner.html',{'owner':owner,'ownerships':owner.ownership_set.select_related('car')})

@login_required
def owner_create(request):
    if not is_staff(request.user): raise PermissionDenied
    form=RegistrationForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        form.save()
        return redirect('owners')
    return render(request,'form.html',{'form':form,'title':'Создать владельца (FBV)'})

class CarList(StaffMixin,ListView):
    model=Car
    template_name='practice/cars.html'
    paginate_by=6
    def get_queryset(self):
        return Car.objects.filter(brand__icontains=self.request.GET.get('q','')[:100])
class CarDetail(StaffMixin,DetailView):
    model=Car
    template_name='practice/car.html'
class CarCreate(StaffMixin,CreateView):
    model=Car
    form_class=CarForm
    template_name='form.html'
    success_url=reverse_lazy('cars')
    extra_context={'title':'Новый автомобиль (CBV)'}
class CarUpdate(StaffMixin,UpdateView):
    model=Car
    form_class=CarForm
    template_name='form.html'
    success_url=reverse_lazy('cars')
    extra_context={'title':'Изменить автомобиль (CBV)'}
class CarDelete(StaffMixin,DeleteView):
    model=Car
    template_name='confirm_delete.html'
    success_url=reverse_lazy('cars')
    extra_context={'back':reverse_lazy('cars')}
