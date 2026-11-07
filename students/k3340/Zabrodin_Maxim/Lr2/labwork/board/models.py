from django.db import models
from django.conf import settings


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Homework(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={"is_staff": True},
    )
    issued_at = models.DateField()
    deadline = models.DateField()
    text = models.TextField()
    fine = models.TextField(blank=True)

    def __str__(self):
        return f"{self.subject} — до {self.deadline}"

class Student_answer(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"is_staff": False},
    )
    text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.PositiveSmallIntegerField(
        choices=[(value, str(value)) for value in range(2, 6)],
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["homework", "student"],
                name="unique_student_homework",
            ),
        ]

    def __str__(self):
        return f"{self.student} — {self.homework}"