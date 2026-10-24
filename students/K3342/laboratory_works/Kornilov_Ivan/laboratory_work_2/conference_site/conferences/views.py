from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from .forms import RegisterForm, ReviewForm, TalkRegistrationForm
from .models import Conference, TalkRegistration, Topic


def query_int(request, name):
    raw = request.GET.get(name, '').strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


class QueryStringMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        context['query'] = params.urlencode()
        return context


class ConferenceListView(QueryStringMixin, ListView):
    model = Conference
    template_name = 'conference_list.html'
    context_object_name = 'conferences'
    paginate_by = 4

    def get_queryset(self):
        queryset = Conference.objects.prefetch_related('topics')
        query = self.request.GET.get('q', '').strip()
        topic = query_int(self.request, 'topic')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(venue_name__icontains=query)
                | Q(description__icontains=query)
                | Q(topics__name__icontains=query)
            ).distinct()
        if topic:
            queryset = queryset.filter(topics__id=topic).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()
        return context


def conference_detail(request, pk):
    conference = get_object_or_404(
        Conference.objects.prefetch_related('topics', 'reviews__author'),
        pk=pk,
    )
    return render(request, 'conference_detail.html', {'conference': conference})


def register(request):
    if request.user.is_authenticated:
        return redirect('conference_list')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('conference_list')
    return render(request, 'registration/register.html', {'form': form})


@login_required
def talk_create(request, conference_id):
    conference = get_object_or_404(Conference, pk=conference_id)
    form = TalkRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        talk = form.save(commit=False)
        talk.user = request.user
        talk.conference = conference
        talk.save()
        messages.success(request, 'Заявка на выступление отправлена')
        return redirect('my_talks')
    return render(request, 'talk_form.html', {'form': form, 'conference': conference})


class MyTalkListView(LoginRequiredMixin, QueryStringMixin, ListView):
    template_name = 'talk_list.html'
    context_object_name = 'talks'
    paginate_by = 6

    def get_queryset(self):
        queryset = TalkRegistration.objects.filter(user=self.request.user).select_related('conference')
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(talk_title__icontains=query) | Q(conference__title__icontains=query)
            )
        return queryset


@login_required
def talk_edit(request, pk):
    talk = get_object_or_404(TalkRegistration, pk=pk, user=request.user)
    form = TalkRegistrationForm(request.POST or None, instance=talk)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Заявка обновлена')
        return redirect('my_talks')
    return render(request, 'talk_form.html', {'form': form, 'talk': talk, 'conference': talk.conference})


@login_required
def talk_delete(request, pk):
    talk = get_object_or_404(TalkRegistration, pk=pk, user=request.user)
    if request.method == 'POST':
        talk.delete()
        messages.success(request, 'Заявка удалена')
        return redirect('my_talks')
    return render(request, 'talk_confirm_delete.html', {'talk': talk})


@login_required
def review_create(request, conference_id):
    conference = get_object_or_404(Conference, pk=conference_id)
    form = ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.conference = conference
        review.author = request.user
        review.conference_start = conference.start_date
        review.conference_end = conference.end_date
        review.save()
        messages.success(request, 'Отзыв опубликован')
        return redirect('conference_detail', pk=conference.pk)
    return render(request, 'review_form.html', {'form': form, 'conference': conference})


class ParticipantListView(QueryStringMixin, ListView):
    template_name = 'participant_list.html'
    context_object_name = 'talks'
    paginate_by = 8

    def get_queryset(self):
        queryset = TalkRegistration.objects.select_related('user', 'conference')
        query = self.request.GET.get('q', '').strip()
        conference = query_int(self.request, 'conference')
        if query:
            queryset = queryset.filter(
                Q(user__username__icontains=query)
                | Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(talk_title__icontains=query)
                | Q(conference__title__icontains=query)
            )
        if conference:
            queryset = queryset.filter(conference_id=conference)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conferences'] = Conference.objects.all()
        return context


@require_POST
@login_required
def set_publication(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden('Недостаточно прав')
    talk = get_object_or_404(TalkRegistration, pk=pk)
    decision = request.POST.get('decision')
    if decision == 'yes':
        talk.recommended_for_publication = True
    elif decision == 'no':
        talk.recommended_for_publication = False
    else:
        return HttpResponseForbidden('Неизвестное решение')
    talk.save(update_fields=['recommended_for_publication'])
    messages.success(request, 'Результат выступления сохранён')
    target = request.POST.get('next', '')
    if target.startswith('/') and not target.startswith('//'):
        return redirect(target)
    return redirect('participants')
