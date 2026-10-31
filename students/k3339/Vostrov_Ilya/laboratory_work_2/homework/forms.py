"""Формы приложения "Доска домашних заданий"."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, Submission


class UserRegistrationForm(UserCreationForm):
    """Регистрация нового пользователя: логин, пароль и учебная группа.

    Учебная группа сохраняется в связанном объекте Profile (модель Profile
    создаётся автоматически при первой записи через update_or_create).
    """

    group = forms.CharField(
        label='Класс / учебная группа',
        max_length=60,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например, K3339',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'group', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control',
                                               'autofocus': True}),
        }
        help_texts = {
            'username': 'Логин для входа на сайт.',
            'password1': 'Пароль должен содержать минимум 8 символов и не быть слишком простым.',
            'password2': 'Повторите пароль для подтверждения.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('password1', 'password2'):
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=commit)
        Profile.objects.update_or_create(
            user=user,
            defaults={'group': self.cleaned_data.get('group', '')},
        )
        return user


class SubmissionForm(forms.ModelForm):
    """Текст сданного решения ученика."""

    class Meta:
        model = Submission
        fields = ('text',)
        labels = {'text': 'Текст решения'}
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Введите текст ответа на задание...',
            }),
        }
