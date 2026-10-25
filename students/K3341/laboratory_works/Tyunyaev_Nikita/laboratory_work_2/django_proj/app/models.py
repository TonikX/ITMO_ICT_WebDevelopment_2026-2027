from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ("student", "Ученик"),
        ("teacher", "Преподаватель / Администратор"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student",
        verbose_name="Роль в системе",
    )
    class_group = models.CharField(
        max_length=50,
        blank=True,
        default="K3341",
        verbose_name="Учебная группа / Класс",
    )
    bio = models.TextField(blank=True, verbose_name="О себе / Дополнительная информация")

    @property
    def is_teacher_user(self) -> bool:
        return self.role == "teacher" or self.is_staff or self.is_superuser

    @property
    def is_student_user(self) -> bool:
        return self.role == "student" and not (self.is_staff or self.is_superuser)

    def __str__(self):
        full_name = self.get_full_name().strip()
        display_name = full_name if full_name else self.username
        return f"{display_name} ({self.get_role_display()})"


class Discipline(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название дисциплины")
    code = models.CharField(max_length=50, blank=True, verbose_name="Код предмета")
    description = models.TextField(blank=True, verbose_name="Описание дисциплины")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Homework(models.Model):
    subject = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        related_name="homeworks",
        verbose_name="Предмет",
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_homeworks",
        verbose_name="Преподаватель",
    )
    title = models.CharField(max_length=200, verbose_name="Тема / Название задания")
    issue_date = models.DateField(default=timezone.now, verbose_name="Дата выдачи")
    due_date = models.DateField(verbose_name="Срок сдачи (дедлайн)")
    description = models.TextField(verbose_name="Текст задания")
    penalty_info = models.TextField(
        default="Штраф: минус 1 балл за каждые полные сутки просрочки сдачи.",
        verbose_name="Информация о штрафах",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"
        ordering = ["-due_date", "-issue_date"]

    def __str__(self):
        return f"[{self.subject.name}] {self.title} (срок: {self.due_date})"

    @property
    def is_past_due(self) -> bool:
        return timezone.now().date() > self.due_date

    @property
    def days_remaining(self) -> int:
        delta = (self.due_date - timezone.now().date()).days
        return delta


class HomeworkSubmission(models.Model):
    STATUS_CHOICES = (
        ("submitted", "На проверке"),
        ("graded", "Оценено"),
        ("returned", "Возвращено на доработку"),
    )

    GRADE_CHOICES = (
        (5, "5 (Отлично)"),
        (4, "4 (Хорошо)"),
        (3, "3 (Удовлетворительно)"),
        (2, "2 (Неудовлетворительно)"),
        (1, "1 (Плохо)"),
    )

    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Домашнее задание",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Ученик",
    )
    answer_text = models.TextField(verbose_name="Текст решения / ответ ученика")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время сдачи")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="submitted",
        verbose_name="Статус проверки",
    )
    grade = models.PositiveSmallIntegerField(
        choices=GRADE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Оценка",
    )
    teacher_comment = models.TextField(
        blank=True,
        verbose_name="Комментарий преподавателя / замечания",
    )
    is_late = models.BooleanField(
        default=False,
        verbose_name="Сдано с опозданием",
    )

    class Meta:
        verbose_name = "Сдача домашнего задания"
        verbose_name_plural = "Сдачи домашних заданий"
        unique_together = ("homework", "student")
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Сдача: {self.student.username} -> {self.homework.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Автоматическая отметка о сдаче после дедлайна
        if self.homework and timezone.now().date() > self.homework.due_date:
            self.is_late = True
        super().save(*args, **kwargs)
