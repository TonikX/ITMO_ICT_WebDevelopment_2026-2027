from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import ConferenceForm, RegistrationForm, ReviewForm
from .models import Conference, Registration, Review, Topic


class ConferenceListView(ListView):
    model = Conference
    template_name = 'conferences/conference_list.html'
    paginate_by = 6

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related('topics')
        topic_id = self.request.GET.get('topic')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        query = self.request.GET.get('q')
        if topic_id:
            qs = qs.filter(topics__id=topic_id)
        if date_from:
            qs = qs.filter(end_date__gte=date_from)
        if date_to:
            qs = qs.filter(start_date__lte=date_to)
        if query:
            qs = qs.filter(title__icontains=query)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()
        context['selected_topic'] = self.request.GET.get('topic', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['query'] = self.request.GET.get('q', '')
        return context


@login_required
def conference_create(request):
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        form = ConferenceForm(request.POST)
        if form.is_valid():
            conference = form.save()
            return redirect('conference_detail', pk=conference.pk)
    else:
        form = ConferenceForm()
    return render(request, 'conferences/conference_form.html', {'form': form})


def _conference_detail_context(request, conference):
    user_registration = None
    if request.user.is_authenticated:
        user_registration = conference.registrations.filter(user=request.user).first()
    return {
        'conference': conference,
        'registrations': conference.registrations.select_related('user'),
        'reviews': conference.reviews.select_related('author'),
        'user_registration': user_registration,
        'registration_form': RegistrationForm(),
        'review_form': ReviewForm(),
    }


def conference_detail(request, pk):
    conference = get_object_or_404(Conference, pk=pk)
    return render(request, 'conferences/conference_detail.html', _conference_detail_context(request, conference))


@login_required
def registration_create(request, pk):
    conference = get_object_or_404(Conference, pk=pk)
    form = RegistrationForm(request.POST)
    if form.is_valid():
        registration = form.save(commit=False)
        registration.conference = conference
        registration.user = request.user
        registration.save()
        return redirect('conference_detail', pk=pk)
    context = _conference_detail_context(request, conference)
    context['registration_form'] = form
    return render(request, 'conferences/conference_detail.html', context)


@login_required
def registration_update(request, pk):
    registration = get_object_or_404(Registration, pk=pk)
    if registration.user != request.user and not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=registration)
        if form.is_valid():
            form.save()
            return redirect('conference_detail', pk=registration.conference_id)
    else:
        form = RegistrationForm(instance=registration)
    return render(request, 'conferences/registration_form.html', {'form': form, 'registration': registration})


@login_required
def registration_delete(request, pk):
    registration = get_object_or_404(Registration, pk=pk)
    if registration.user != request.user and not request.user.is_staff:
        raise PermissionDenied
    conference_id = registration.conference_id
    if request.method == 'POST':
        registration.delete()
        return redirect('conference_detail', pk=conference_id)
    return render(request, 'conferences/registration_confirm_delete.html', {'registration': registration})


@login_required
def review_create(request, pk):
    conference = get_object_or_404(Conference, pk=pk)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.conference = conference
        review.author = request.user
        review.save()
        return redirect('conference_detail', pk=pk)
    context = _conference_detail_context(request, conference)
    context['review_form'] = form
    return render(request, 'conferences/conference_detail.html', context)


@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.author != request.user and not request.user.is_staff:
        raise PermissionDenied
    conference_id = review.conference_id
    if request.method == 'POST':
        review.delete()
        return redirect('conference_detail', pk=conference_id)
    return render(request, 'conferences/review_confirm_delete.html', {'review': review})


class ParticipantsListView(ListView):
    template_name = 'conferences/participants.html'
    paginate_by = 10
    queryset = Registration.objects.select_related('user', 'conference').order_by('-created_at')


@login_required
def registration_set_recommendation(request, pk):
    registration = get_object_or_404(Registration, pk=pk)
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        value = request.POST.get('recommended_for_publication')
        registration.recommended_for_publication = {'yes': True, 'no': False}.get(value)
        registration.save(update_fields=['recommended_for_publication'])
    return redirect(request.META.get('HTTP_REFERER') or 'participants')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('conference_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
