from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q, Sum, Count, F, DecimalField, ExpressionWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Tour, Booking, Review
from .forms import TourForm, BookingForm, ReviewForm, SearchForm, BookingSearchForm, SalesSearchForm
from .services import confirm_booking

def is_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)
class StaffMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self): return is_staff(self.request.user)

def paginate(request, queryset):
    return Paginator(queryset, 6).get_page(request.GET.get('page'))

class TourList(ListView):
    model = Tour
    template_name = 'tours/list.html'
    context_object_name = 'tours'
    paginate_by = 6
    def get_queryset(self):
        qs = Tour.objects.select_related('country','agency')
        if not is_staff(self.request.user): qs = qs.filter(is_active=True)
        self.form = SearchForm(self.request.GET)
        if not self.form.is_valid(): return qs.none()
        d = self.form.cleaned_data
        if d['q']: qs = qs.filter(Q(title__icontains=d['q'])|Q(description__icontains=d['q']))
        for key in ('country','agency'):
            if d[key]: qs = qs.filter(**{key:d[key]})
        if d['date_from']: qs = qs.filter(start_date__gte=d['date_from'])
        if d['date_to']: qs = qs.filter(start_date__lte=d['date_to'])
        if d['max_price'] is not None: qs = qs.filter(price__lte=d['max_price'])
        return qs.order_by(d['sort'] or 'start_date','pk')
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = self.form
        return ctx

class TourDetail(DetailView):
    model = Tour
    template_name = 'tours/detail.html'
    context_object_name = 'tour'
    def get_queryset(self):
        qs = Tour.objects.select_related('agency','country')
        return qs if is_staff(self.request.user) else qs.filter(is_active=True)
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['reviews'] = paginate(self.request, self.object.review_set.select_related('user'))
        ctx['today'] = timezone.localdate()
        return ctx

class TourCreate(StaffMixin, CreateView):
    model = Tour
    form_class = TourForm
    template_name = 'form.html'
    success_url = reverse_lazy('tour_list')
    extra_context = {'title':'Новый тур'}
class TourUpdate(StaffMixin, UpdateView):
    model = Tour
    form_class = TourForm
    template_name = 'form.html'
    success_url = reverse_lazy('tour_list')
    extra_context = {'title':'Редактирование тура'}

@login_required
def book(request, pk):
    tour = get_object_or_404(Tour, pk=pk, is_active=True)
    if tour.start_date < timezone.localdate():
        messages.error(request,'Этот тур уже начался.')
        return redirect('tour_detail', pk=pk)
    if Booking.objects.filter(user=request.user,tour=tour).exists():
        messages.info(request,'Бронирование уже существует. Измените его в личном кабинете.')
        return redirect('my_bookings')
    form = BookingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False)
        booking.user, booking.tour, booking.unit_price = request.user, tour, tour.price
        try:
            with transaction.atomic(): booking.save()
        except IntegrityError:
            form.add_error(None,'Бронирование уже существует.')
        else:
            messages.success(request,'Заявка отправлена. Ожидайте подтверждения.')
            return redirect('my_bookings')
    return render(request,'form.html',{'form':form,'title':f'Бронирование: {tour.title}'})

@login_required
def booking_list(request):
    form = BookingSearchForm(request.GET)
    qs = Booking.objects.filter(user=request.user).select_related('tour','tour__country')
    if form.is_valid():
        d=form.cleaned_data
        if d['q']: qs=qs.filter(tour__title__icontains=d['q'])
        if d['status']: qs=qs.filter(status=d['status'])
    else: qs=qs.none()
    return render(request,'tours/bookings.html',{'page_obj':paginate(request,qs),'form':form,'title':'Мои бронирования'})

@login_required
def booking_edit(request, pk):
    # Блокировка исключает потерю одновременного подтверждения/редактирования.
    with transaction.atomic():
        booking = get_object_or_404(Booking.objects.select_for_update(),pk=pk,user=request.user)
        form = BookingForm(request.POST or None,instance=booking)
        if request.method == 'POST' and form.is_valid():
            booking=form.save(commit=False)
            booking.status=Booking.PENDING
            booking.save()
            messages.success(request,'Изменения сохранены. Требуется повторное подтверждение.')
            return redirect('my_bookings')
    return render(request,'form.html',{'form':form,'title':'Изменить бронирование'})

@login_required
def booking_delete(request, pk):
    booking=get_object_or_404(Booking,pk=pk,user=request.user)
    if request.method=='POST':
        booking.delete()
        messages.success(request,'Бронирование удалено.')
        return redirect('my_bookings')
    return render(request,'confirm_delete.html',{'object':booking,'back':reverse_lazy('my_bookings')})

@login_required
def review_create(request, pk):
    tour=get_object_or_404(Tour,pk=pk,is_active=True)
    form=ReviewForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        review=form.save(commit=False)
        review.user,review.tour=request.user,tour
        review.start_date,review.end_date=tour.start_date,tour.end_date
        try:
            with transaction.atomic(): review.save()
        except IntegrityError: form.add_error(None,'Вы уже оставили отзыв об этом туре.')
        else:
            messages.success(request,'Спасибо за отзыв!')
            return redirect('tour_detail',pk=pk)
    return render(request,'form.html',{'form':form,'title':f'Отзыв: {tour.title}'})

@login_required
def staff_bookings(request):
    if not is_staff(request.user): raise PermissionDenied
    form=BookingSearchForm(request.GET)
    qs=Booking.objects.select_related('tour','user','tour__country')
    if form.is_valid():
        d=form.cleaned_data
        if d['q']: qs=qs.filter(tour__title__icontains=d['q'])
        if d['status']: qs=qs.filter(status=d['status'])
    else: qs=qs.none()
    return render(request,'tours/bookings.html',{'page_obj':paginate(request,qs),'form':form,'title':'Заявки туристов','staff_mode':True})

@require_POST
@login_required
def booking_confirm(request,pk):
    if not is_staff(request.user): raise PermissionDenied
    get_object_or_404(Booking,pk=pk)
    confirm_booking(pk)
    messages.success(request,'Бронирование подтверждено.')
    return redirect('staff_bookings')

@login_required
def sales(request):
    if not is_staff(request.user): raise PermissionDenied
    form=SalesSearchForm(request.GET)
    qs=Booking.objects.filter(status=Booking.CONFIRMED)
    if form.is_valid():
        d=form.cleaned_data
        if d['q']: qs=qs.filter(tour__title__icontains=d['q'])
        if d['country']: qs=qs.filter(tour__country=d['country'])
    else: qs=qs.none()
    total=ExpressionWrapper(F('unit_price')*F('travelers'), output_field=DecimalField(max_digits=14,decimal_places=2))
    rows=qs.values('tour__country__name','tour__title','tour_id','tour__start_date','tour__end_date').annotate(
        reservations=Count('id'), travelers_count=Sum('travelers'), revenue=Sum(total)).order_by('tour__country__name','tour__title','tour_id')
    summary=qs.values('tour__country__name').annotate(reservations=Count('id'),travelers_count=Sum('travelers'),revenue=Sum(total)).order_by('tour__country__name')
    return render(request,'tours/sales.html',{'form':form,'page_obj':paginate(request,rows),'summary':summary})
