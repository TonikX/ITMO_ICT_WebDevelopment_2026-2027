from django.conf import settings
from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Homework(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="homeworks")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="homeworks")
    issued = models.DateField(verbose_name="дата выдачи")
    due = models.DateField(verbose_name="срок выполнения")
    text = models.TextField(verbose_name="текст задания")
    penalties = models.TextField(verbose_name="штрафы", blank=True)

    def __str__(self):
        return "{} ({})".format(self.subject, self.issued)


class Submission(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    text = models.TextField()
    submitted_at = models.DateTimeField(auto_now=True)
    grade = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("homework", "student")

    def __str__(self):
        return "{} - {}".format(self.homework, self.student)
