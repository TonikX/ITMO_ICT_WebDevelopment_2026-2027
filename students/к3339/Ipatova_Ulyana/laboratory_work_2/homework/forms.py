from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Homework, StudyGroup, Submission


class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='Имя', max_length=150)
    last_name = forms.CharField(label='Фамилия', max_length=150)
    patronymic = forms.CharField(label='Отчество', max_length=150)
    email = forms.EmailField(label='Электронная почта')
    study_group = forms.ModelChoiceField(
        label='Учебная группа',
        queryset=StudyGroup.objects.order_by('group_name'),
        empty_label='Выберите свою группу',
    )

    class Meta(UserCreationForm.Meta):
        fields = (
            'username', 'first_name', 'last_name', 'patronymic',
            'email', 'study_group', 'password1', 'password2',
        )
        labels = {'username': 'Логин'}


class SubmissionForm(forms.Form):
    answer_text = forms.CharField(
        label='Текст ответа',
        widget=forms.Textarea(attrs={'rows': 8}),
        error_messages={'required': 'Введите текст ответа. Ответ не может быть пустым.'},
    )


class HomeworkForm(forms.ModelForm):
    fixed_fields = ('subject', 'study_group', 'issue_at', 'deadline')

    class Meta:
        model = Homework
        fields = ('subject', 'study_group', 'issue_at', 'deadline', 'description', 'penalty_info')
        labels = {
            'subject': 'Дисциплина',
            'study_group': 'Учебная группа',
            'issue_at': 'Дата выдачи',
            'deadline': 'Срок сдачи',
            'description': 'Текст задания',
            'penalty_info': 'Информация о штрафах',
            'teacher': 'Преподаватель',
        }
        widgets = {
            'issue_at': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'deadline': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 6}),
            'penalty_info': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_submissions = False
        if self.instance.pk:
            self.has_submissions = self.instance.submissions.exists()
        if self.has_submissions:
            for field_name in self.fixed_fields:
                if field_name in self.fields:
                    self.fields[field_name].disabled = True


class GradeForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('grade',)
        labels = {'grade': 'Оценка'}
        help_texts = {'grade': 'Допустимые оценки: от 2 до 5.'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grade'].required = True
