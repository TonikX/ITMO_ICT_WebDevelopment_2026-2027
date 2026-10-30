from django.conf import settings 
from django.core.exceptions import ValidationError 
from django.core.validators import MinValueValidator, MaxValueValidator 
from django.db import models
from django.utils import timezone 

class StudyGroup(models.Model):
    group_name = models.CharField(
        max_length=50,
        unique=True
    )
    def __str__(self):
        return self.group_name


class Subject(models.Model):
    subject_name = models.CharField(
        max_length=150,
        unique=True
    )
    def __str__(self):
        return self.subject_name

class StudentProfile(models.Model):
    patronymic = models.CharField(max_length=150, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    study_group = models.ForeignKey(
            StudyGroup,
            on_delete=models.PROTECT,
            related_name='students'
    )

    def __str__(self):
        return self.user.username

class Homework(models.Model):
    description = models.TextField()
    issue_at = models.DateField(default=timezone.localdate)
    deadline = models.DateField()
    penalty_info = models.TextField(blank=True)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name='homeworks'
    )
    study_group = models.ForeignKey(
        StudyGroup,
        on_delete=models.PROTECT,
        related_name='homeworks'
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='assigned_homeworks'
    )
    def clean(self):
        super().clean()
        if self.issue_at and self.deadline:
            if self.deadline < self.issue_at:
                raise ValidationError({'deadline': 'Срок сдачи не может быть раньше даты выдачи!!'})
        if self.teacher_id:
            if not self.teacher.is_staff:
                raise ValidationError({'teacher': 'Преподаватель должен иметь статус is_staff'})
            
    def __str__(self):
            return f'{self.subject.subject_name} - {self.study_group.group_name} - {self.deadline}'
    class Meta:
        ordering = ['deadline']

class Submission(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='submissions'
    )
    homework = models.ForeignKey(
        Homework,
        on_delete=models.PROTECT,
        related_name='submissions'
    )
    answer_text = models.TextField()
    submitted_at = models.DateTimeField(
        auto_now_add=True
    )
    grade = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(2), MaxValueValidator(5)]
    )

    def clean(self):
        super().clean()
        if self.student_id and self.homework_id:
            if self.student.is_staff:
                raise ValidationError('Преподаватель не должен сдавать домашнее задание')
            try:
                profile = self.student.student_profile
            except StudentProfile.DoesNotExist:
                raise ValidationError('У пользователя нет профиля ученика')

            if profile.study_group_id != self.homework.study_group_id:
                raise ValidationError('Это задание для другой группы')
    def __str__(self):
                return f'{self.student.username} - {self.homework.subject.subject_name}'
    class Meta:
        constraints = [
             models.UniqueConstraint(
                  fields=['student', 'homework'],
                  name='unique_student_homework_submission'
             )
        ] 



