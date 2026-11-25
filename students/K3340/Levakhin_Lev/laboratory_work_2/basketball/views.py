from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.db.models import Q
from django.contrib.auth import login
from .models import Team, Match, Prediction, Comment
from .forms import CustomUserCreationForm, PredictionForm, CommentForm, MatchStatusForm


class TeamListView(ListView):
    model = Team
    template_name = 'basketball/team_list.html'
    context_object_name = 'teams'

class TeamDetailView(DetailView):
    model = Team
    template_name = 'basketball/team_detail.html'
    context_object_name = 'team'

class MatchListView(ListView):
    model = Match
    template_name = 'basketball/match_list.html'
    context_object_name = 'matches'
    ordering = ['-date']


class MatchDetailView(View):
    def get(self, request, pk):
        match = get_object_or_404(Match, pk=pk)
        comments = match.comments.all().order_by('-created_at')

        user_prediction = None
        if request.user.is_authenticated:
            user_prediction = Prediction.objects.filter(user=request.user, match=match).first()

        context = {
            'match': match,
            'comments': comments,
            'prediction_form': PredictionForm(instance=user_prediction),
            'comment_form': CommentForm(),
            'user_prediction': user_prediction,
            'status_form': MatchStatusForm(instance=match) if request.user.is_staff else None,
        }
        return render(request, 'basketball/match_detail.html', context)

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return redirect('basketball:login')

        match = get_object_or_404(Match, pk=pk)

        # Форма статуса для админа
        if 'submit_status' in request.POST and request.user.is_staff:
            form = MatchStatusForm(request.POST, instance=match)
            if form.is_valid():
                form.save()
                return redirect('basketball:match_detail', pk=match.pk)

        # Обработка прогноза
        if 'submit_prediction' in request.POST:
            instance = Prediction.objects.filter(user=request.user, match=match).first()
            form = PredictionForm(request.POST, instance=instance)
            if form.is_valid():
                prediction = form.save(commit=False)
                prediction.user = request.user
                prediction.match = match
                prediction.save()
                return redirect('basketball:match_detail', pk=match.pk)

        # Обработка комментария
        elif 'submit_comment' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.match = match
                comment.save()
                return redirect('basketball:match_detail', pk=match.pk)

        return redirect('basketball:match_detail', pk=match.pk)


class BasketballMatchListView(ListView):
    model = Match
    template_name = 'basketball/match_list.html'
    context_object_name = 'matches'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-date')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(home_team__name__icontains=search_query) |
                Q(away_team__name__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('basketball:team_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'basketball/register.html', {'form': form})