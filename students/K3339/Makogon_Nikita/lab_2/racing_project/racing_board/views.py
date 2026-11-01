from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from .models import Race, RaceRegistration, Comment
from .forms import RacerRegistrationForm, RaceEnrollForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.db.models import Q


# главная страница: список всех гонок
class RaceListView(ListView):
    model = Race
    template_name = 'racing_board/race_list.html'
    context_object_name = 'races'
    paginate_by = 2  # пагинация по 2 гонки
    
    def get_queryset(self):
        queryset = Race.objects.all().order_by('is_completed', '-race_date')
        
        # получаем запрос из поисковой строки
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(track__icontains=search_query)
            )
        return queryset

# детальная страница гонки (информация + зарегистрированные участники)
class RaceDetailView(DetailView):
    model = Race
    template_name = 'racing_board/race_detail.html'
    context_object_name = 'race'


# регистрация нового гонщика
class RegisterView(CreateView):
    form_class = RacerRegistrationForm
    template_name = 'racing_board/register.html'
    success_url = reverse_lazy('login')


# запись гонщика на конкретный заезд
class RaceEnrollView(LoginRequiredMixin, CreateView):
    model = RaceRegistration
    form_class = RaceEnrollForm
    template_name = 'racing_board/race_enroll.html'

    def form_valid(self, form):
        # получаем гонку по ID из URL и привязываем её к форме
        race = get_object_or_404(Race, pk=self.kwargs['pk'])
        form.instance.race = race
        # привязываем текущего авторизованного пользователя
        form.instance.racer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        # после успешной записи возвращаем на страницу этой же гонки
        return reverse_lazy('race_detail', kwargs={'pk': self.kwargs['pk']})


# оставление комментария к гонке
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'racing_board/comment_form.html'

    def form_valid(self, form):
        race = get_object_or_404(Race, pk=self.kwargs['pk'])
        form.instance.race = race
        form.instance.author = self.request.user
        form.instance.race_date = race.race_date  # берём дату из гонки
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('race_detail', kwargs={'pk': self.kwargs['pk']})