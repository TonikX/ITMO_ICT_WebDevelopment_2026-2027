
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import SchoolClass, Assignment, Submission


class StudentRegistrationForm(UserCreationForm):
    school_class = forms.ModelChoiceField(
        queryset=SchoolClass.objects.all(),
        label="Класс",
        empty_label="Выберите класс"
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "school_class",
        )
        labels = {
            "username": "Логин",
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs["class"] = (
                "form-select" if name == "school_class"
                else "form-control"
            )


class StudentLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["answer"]
        labels = {"answer": "Ваш ответ"}
        widgets = {
            "answer": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "Введите решение задания..."
            })
        }


class GradeForm(forms.ModelForm):
    grade = forms.IntegerField(
        label="Оценка",
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={
            "class": "form-control"
        })
    )

    class Meta:
        model = Submission
        fields = ["grade", "teacher_comment"]
        labels = {
            "teacher_comment": "Комментарий преподавателя"
        }
        widgets = {
            "teacher_comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            })
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            "title",
            "description",
            "subject",
            "school_class",
            "due_date",
        ]
        labels = {
            "title": "Название задания",
            "description": "Описание задания",
            "subject": "Предмет",
            "school_class": "Класс",
            "due_date": "Срок сдачи",
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6
            }),
            "subject": forms.Select(attrs={
                "class": "form-select"
            }),
            "school_class": forms.Select(attrs={
                "class": "form-select"
            }),
            "due_date": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
        }
