from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Discipline, Homework, HomeworkSubmission

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label="Имя")
    last_name = forms.CharField(max_length=50, required=True, label="Фамилия")
    email = forms.EmailField(required=True, label="Email")
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        label="Роль в системе",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    class_group = forms.CharField(
        max_length=50,
        required=False,
        initial="K3341",
        label="Класс / Группа",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Например: K3341"}),
    )
    bio = forms.CharField(
        required=False,
        label="О себе",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Краткая информация..."}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "class_group",
            "bio",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ["username", "email", "first_name", "last_name"]:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({"class": "form-control"})


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "class_group", "bio")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "class_group": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ("subject", "title", "issue_date", "due_date", "description", "penalty_info")
        widgets = {
            "subject": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Например: Лабораторная работа №2"}),
            "issue_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": "Подробное описание задания..."}),
            "penalty_info": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Информация о штрафах за просрочку..."}),
        }


class HomeworkSubmissionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ("answer_text",)
        widgets = {
            "answer_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                    "placeholder": "Введите текст вашего решения, ссылки на репозиторий, пояснения или ответы на вопросы...",
                }
            )
        }


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = HomeworkSubmission
        fields = ("grade", "status", "teacher_comment")
        widgets = {
            "grade": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "teacher_comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Комментарий преподавателя к выставленной оценке...",
                }
            ),
        }
