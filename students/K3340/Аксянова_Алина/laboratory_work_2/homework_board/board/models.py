from django.db import models
from django.conf import settings
from django.utils import timezone

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Homework(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_date = models.DateField(default=timezone.localdate)
    start_date = models.DateField()
    due_date = models.DateField()
    description = models.TextField()
    penalty_info = models.TextField(blank=True)

    def __str__(self):
        return f"{self.subject} - {self.description[:30]}"


class Submission(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    answer_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.homework}"
