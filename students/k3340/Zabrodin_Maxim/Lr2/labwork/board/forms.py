from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Student_answer,Homework


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name"]
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Student_answer
        fields = ["text"]
        labels = {"text": "Ваш ответ"}
class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        fields = ["subject", "issued_at", "deadline", "text", "fine"]
        labels = {
            "subject": "Предмет",
            "issued_at": "Дата выдачи",
            "deadline": "Срок сдачи",
            "text": "Текст задания",
            "fine": "Штрафы",
        }
        widgets = {
            "issued_at": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
            "deadline": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
        }

    def clean(self):
        data = super().clean()
        issued_at = data.get("issued_at")
        deadline = data.get("deadline")

        if issued_at and deadline and deadline < issued_at:
            self.add_error("deadline", "Срок сдачи раньше даты выдачи.")

        return data