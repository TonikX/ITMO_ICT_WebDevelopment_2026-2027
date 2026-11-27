from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone

from .forms import RegistrationForm, FeedbackForm
from .models import Conference, Registration, Feedback, Topic


# Create your views here.

def register_page(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form })

def login_page(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form })

def logout_page(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
    return redirect('/')

def conference_detail(request, conference_id):
    conference = get_object_or_404(Conference, pk=conference_id)
    feedbacks = Feedback.objects.filter(conference_id=conference_id).order_by('-date')
    feedback_form = FeedbackForm()
    return render(request, 'conference_detail.html',
                  {'conference': conference, 'feedbacks': feedbacks, 'feedback_form': feedback_form })

def conference_list(request):
    all_conferences = Conference.objects.order_by('-start_date')

    # Поиск по названию и описанию
    q = request.GET.get('q', '').strip()
    if q:
        all_conferences = all_conferences.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )

    # Фильтр по тематике
    topic_id = request.GET.get('topic', '')
    if topic_id.isdigit():
        all_conferences = all_conferences.filter(topics__id=topic_id)

    # Фильтр по времени
    period = request.GET.get('period', '')
    now = timezone.now()
    if period == 'upcoming':
        all_conferences = all_conferences.filter(end_date__gte=now)
    elif period == 'past':
        all_conferences = all_conferences.filter(end_date__lt=now)

    paginator = Paginator(all_conferences, 10)
    page_num = request.GET.get('page', 1)
    try:
        # Если существует, то выбираем эту страницу
        current_conferences = paginator.page(page_num)
    except PageNotAnInteger:
        # Если не число
        current_conferences = paginator.page(1)
    except EmptyPage:
        # Если вышли за последнюю страницу, то возвращаем последнюю
        current_conferences = paginator.page(paginator.num_pages)

    # Параметры фильтров для ссылок пагинации (без page)
    params = request.GET.copy()
    params.pop('page', None)

    return render(request, 'conference_list.html', {
        'conferences': current_conferences,
        'topics': Topic.objects.order_by('name'),
        'querystring': params.urlencode(),
    })


@login_required
def registration_report_create(request, conference_id):
    conference = get_object_or_404(Conference, pk=conference_id)
    if request.method == 'POST':
        form = RegistrationForm(request.POST, conference=conference)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.conference = conference
            registration.user = request.user
            registration.save()
            form.save_m2m()
            return redirect('/registrations/')
    else:
        form = RegistrationForm(conference=conference)
    return render(request, 'registration_report_form.html',
    {
        'form': form,
        'conference': conference,
        'is_edit': False,
    })

@login_required
def registration_report_edit(request, registration_id):
    registration = get_object_or_404(Registration, pk=registration_id, user=request.user)
    conference = registration.conference
    if request.method == 'POST':
        form = RegistrationForm(request.POST, conference=conference, instance=registration)
        if form.is_valid():
            form.save()
            return redirect('/registrations/')
    else:
        form = RegistrationForm(conference=conference, instance=registration)
    return render(request, 'registration_report_form.html',
    {
        'form': form,
        'conference': conference,
        'is_edit': True,
    })

@login_required
def registration_report_delete(request, registration_id):
    registration = get_object_or_404(Registration, pk=registration_id, user=request.user)
    if request.method == 'POST':
        registration.delete()
    return redirect('/registrations/')

@login_required
def registration_report_list(request):
    registrations = Registration.objects.filter(user=request.user) \
        .select_related('conference').prefetch_related('topics').order_by('-registration_date')
    return render(request, 'my_registrations.html', {'registrations': registrations })


@login_required
def feedback_create(request, conference_id):
    if request.method == 'POST':
        conference = get_object_or_404(Conference, pk=conference_id)
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.conference = conference
            feedback.save()
    return redirect(f'/conference/{conference_id}/')



@login_required
def feedback_delete(request, feedback_id):
    feedback = get_object_or_404(Feedback, pk=feedback_id)
    conference_id = feedback.conference.id
    if not request.user.is_staff:
        raise Http404()
    if request.method == 'POST':
        feedback.delete()
    return redirect(f'/conference/{conference_id}/')


def participants_table(request, conference_id):
    conference = get_object_or_404(Conference, pk=conference_id)
    if request.user.is_staff:
        registrations = Registration.objects.filter(conference_id=conference_id)
    else:
        registrations = Registration.objects.filter(conference_id=conference_id, status=Registration.Status.APPROVED)
    return render(request, 'conference_participants.html',
                  {'registrations': registrations, 'conference': conference})


@login_required
@require_POST
def registration_update_status(request, registration_id):
    if not request.user.is_staff:
        raise PermissionDenied
    registration = get_object_or_404(Registration, pk=registration_id)

    status = request.POST.get('status')
    if status in Registration.Status.values:
        registration.status = status
        if status != Registration.Status.APPROVED:
            registration.is_recommended = None

    result_values = {'': None, 'true': True, 'false': False}
    result = request.POST.get('result')
    if result in result_values and registration.status == Registration.Status.APPROVED:
        registration.is_recommended = result_values[result]

    registration.save(update_fields=['status', 'is_recommended'])
    return redirect(f'/conference/{registration.conference.id}/participants/')