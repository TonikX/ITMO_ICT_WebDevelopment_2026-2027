from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import (
    GradeSubmissionForm,
    HomeworkForm,
    HomeworkSubmissionForm,
    UserProfileForm,
    UserRegistrationForm,
)
from .models import Discipline, Homework, HomeworkSubmission

User = get_user_model()


class TeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Миксин для проверки прав преподавателя / администратора"""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_staff or user.role == "teacher" or user.is_superuser)

    def handle_no_permission(self):
        messages.error(self.request, "Данное действие доступно только преподавателю или администратору.")
        return redirect("homework_list")


class UserRegisterView(CreateView):
    """Регистрация нового пользователя"""

    model = User
    form_class = UserRegistrationForm
    template_name = "register.html"
    success_url = reverse_lazy("homework_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f"Добро пожаловать, {self.object.username}! Регистрация прошла успешно.")
        return response


class UserLoginView(LoginView):
    """Вход в систему"""

    template_name = "login.html"

    def form_valid(self, form):
        messages.success(self.request, f"Рады видеть вас снова, {form.get_user().username}!")
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    """Выход из системы"""

    next_page = reverse_lazy("homework_list")

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "Вы вышли из учетной записи.")
        return super().dispatch(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, UpdateView):
    """Просмотр и редактирование личного профиля"""

    model = User
    form_class = UserProfileForm
    template_name = "profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.role == "student":
            submissions = HomeworkSubmission.objects.filter(student=user).select_related("homework", "homework__subject")
            context["my_submissions"] = submissions
            context["my_avg_grade"] = submissions.filter(grade__isnull=False).aggregate(Avg("grade"))["grade__avg"]
        elif user.is_teacher_user:
            context["created_homeworks"] = Homework.objects.filter(teacher=user).select_related("subject")
        return context

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлен.")
        return super().form_valid(form)


class HomeworkListView(ListView):
    """Просмотр всех домашних заданий с пагинацией, поиском и фильтрацией"""

    model = Homework
    template_name = "homework_list.html"
    context_object_name = "homeworks"
    paginate_by = 6

    def get_queryset(self):
        qs = Homework.objects.select_related("subject", "teacher").all()

        # Поиск по названию или тексту задания
        query = self.request.GET.get("q", "").strip()
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))

        # Фильтрация по дисциплине
        subject_id = self.request.GET.get("subject", "").strip()
        if subject_id:
            qs = qs.filter(subject_id=subject_id)

        # Фильтрация по статусу дедлайна
        status_filter = self.request.GET.get("status", "").strip()
        if status_filter == "active":
            from django.utils import timezone

            qs = qs.filter(due_date__gte=timezone.now().date())
        elif status_filter == "expired":
            from django.utils import timezone

            qs = qs.filter(due_date__lt=timezone.now().date())

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["disciplines"] = Discipline.objects.all()
        context["current_q"] = self.request.GET.get("q", "")
        context["current_subject"] = self.request.GET.get("subject", "")
        context["current_status"] = self.request.GET.get("status", "")

        # Если пользователь ученик — прикрепляем словарь с его сдачами {homework_id: submission}
        if self.request.user.is_authenticated and not self.request.user.is_teacher_user:
            student_submissions = HomeworkSubmission.objects.filter(
                student=self.request.user
            ).values("homework_id", "status", "grade")
            context["user_submissions"] = {s["homework_id"]: s for s in student_submissions}

        return context


class HomeworkDetailView(DetailView):
    """Детальный просмотр задания, сдача работы (для ученика) и просмотр сдач (для учителя)"""

    model = Homework
    template_name = "homework_detail.html"
    context_object_name = "homework"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        homework = self.object
        user = self.request.user

        if user.is_authenticated:
            if user.is_teacher_user:
                # Преподаватель видит все сдачи этого задания
                submissions = homework.submissions.select_related("student").order_by("-submitted_at")
                context["submissions"] = submissions
                context["grade_form"] = GradeSubmissionForm()
            else:
                # Ученик видит свою сдачу и форму для отправки / редактирования
                try:
                    my_submission = HomeworkSubmission.objects.get(homework=homework, student=user)
                    context["my_submission"] = my_submission
                    context["submission_form"] = HomeworkSubmissionForm(instance=my_submission)
                except HomeworkSubmission.DoesNotExist:
                    context["my_submission"] = None
                    context["submission_form"] = HomeworkSubmissionForm()

        return context


class HomeworkCreateView(TeacherRequiredMixin, CreateView):
    """Создание нового домашнего задания (только для преподавателей/администраторов)"""

    model = Homework
    form_class = HomeworkForm
    template_name = "homework_form.html"

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        messages.success(self.request, "Домашнее задание успешно создано и опубликовано!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("homework_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action_title"] = "Создание нового домашнего задания"
        context["button_text"] = "Опубликовать задание"
        return context


class HomeworkUpdateView(TeacherRequiredMixin, UpdateView):
    """Редактирование домашнего задания (только для преподавателей/администраторов)"""

    model = Homework
    form_class = HomeworkForm
    template_name = "homework_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Домашнее задание успешно обновлено.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("homework_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action_title"] = f"Редактирование: {self.object.title}"
        context["button_text"] = "Сохранить изменения"
        return context


class HomeworkDeleteView(TeacherRequiredMixin, DeleteView):
    """Удаление домашнего задания"""

    model = Homework
    template_name = "homework_confirm_delete.html"
    success_url = reverse_lazy("homework_list")

    def delete(self, request, *args, **kwargs):
        messages.info(request, "Домашнее задание удалено.")
        return super().delete(request, *args, **kwargs)


@login_required
def submit_homework(request, pk):
    """Сдача домашнего задания в текстовом виде (FBV)"""
    homework = get_object_or_404(Homework, pk=pk)
    user = request.user

    if user.is_teacher_user:
        messages.warning(request, "Преподаватели не могут сдавать решения.")
        return redirect("homework_detail", pk=pk)

    if request.method == "POST":
        submission, created = HomeworkSubmission.objects.get_or_create(
            homework=homework,
            student=user,
            defaults={"answer_text": ""},
        )
        form = HomeworkSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.status = "submitted"  # сбрасываем в 'на проверке' при обновлении решения
            sub.save()
            msg = "Ваше решение успешно сдано на проверку!" if created else "Ваше решение обновлено."
            messages.success(request, msg)
        else:
            messages.error(request, "Пожалуйста, проверьте введённые данные.")

    return redirect("homework_detail", pk=pk)


@login_required
def grade_submission(request, pk):
    """Выставление оценки преподавателем через клиентский интерфейс (FBV)"""
    submission = get_object_or_404(HomeworkSubmission, pk=pk)
    user = request.user

    if not (user.is_staff or user.role == "teacher" or user.is_superuser):
        messages.error(request, "У вас нет прав для оценивания работ.")
        return redirect("homework_detail", pk=submission.homework.pk)

    if request.method == "POST":
        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Оценка для ученика {submission.student.get_full_name() or submission.student.username} успешно сохранена!",
            )
        else:
            messages.error(request, "Ошибка при выставлении оценки.")

    return redirect("homework_detail", pk=submission.homework.pk)


class GradebookView(LoginRequiredMixin, TemplateView):
    """Сводная таблица оценок всех учеников класса (Классный журнал)"""

    template_name = "gradebook.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Выборка дисциплин
        disciplines = Discipline.objects.all()
        selected_subject_id = self.request.GET.get("subject", "").strip()

        homeworks_qs = Homework.objects.select_related("subject").order_by("due_date")
        if selected_subject_id:
            homeworks_qs = homeworks_qs.filter(subject_id=selected_subject_id)

        homeworks = list(homeworks_qs)

        # Получаем всех учеников
        students = User.objects.filter(Q(role="student") | Q(submissions__isnull=False)).distinct().order_by("last_name", "first_name", "username")

        # Получаем все сдачи
        submissions = HomeworkSubmission.objects.filter(homework__in=homeworks).select_related("student", "homework")

        # Составляем карту сдач: (student_id, homework_id) -> submission
        sub_map = {(s.student_id, s.homework_id): s for s in submissions}

        # Формируем матрицу для отображения
        grade_matrix = []
        for student in students:
            student_row = {
                "student": student,
                "grades": [],
                "avg_grade": None,
            }
            total_score = 0
            graded_count = 0

            for hw in homeworks:
                sub = sub_map.get((student.id, hw.id))
                if sub and sub.grade is not None:
                    total_score += sub.grade
                    graded_count += 1
                student_row["grades"].append({
                    "homework": hw,
                    "submission": sub,
                })

            if graded_count > 0:
                student_row["avg_grade"] = round(total_score / graded_count, 2)

            grade_matrix.append(student_row)

        context["disciplines"] = disciplines
        context["selected_subject_id"] = selected_subject_id
        context["homeworks"] = homeworks
        context["grade_matrix"] = grade_matrix
        return context
