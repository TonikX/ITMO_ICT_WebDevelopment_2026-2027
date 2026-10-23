from django.conf import settings
from django.db import models


class Subject(models.Model):
    """
    A school subject, e.g. "Mathematics". Kept as its own small table
    (instead of just a text field on Homework) so we can show a clean
    dropdown filter and avoid typos like "Math" vs "math" vs "Maths".
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        # This is what shows up in the admin panel and in <select> dropdowns
        return self.name


class Homework(models.Model):
    """
    One homework assignment. Created by the teacher through Django Admin
    (the assignment doesn't ask students to create homeworks themselves).
    """
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='homeworks')
    teacher_name = models.CharField(max_length=100)
    date_given = models.DateField()
    deadline = models.DateField()
    text = models.TextField(help_text="What the student needs to do")
    penalty_info = models.CharField(
        max_length=200,
        blank=True,
        help_text="What happens if submitted late, e.g. '-10% per day late'"
    )

    class Meta:
        ordering = ['-deadline']

    def __str__(self):
        return f"{self.subject} — {self.text[:40]}"


class Submission(models.Model):
    """
    A single student's answer to a single homework.
    One (student, homework) pair should only submit once, hence unique_together.
    """
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Left blank until the teacher grades it via Django Admin
    grade = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        unique_together = ('homework', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} -> {self.homework} ({self.grade or 'not graded'})"
