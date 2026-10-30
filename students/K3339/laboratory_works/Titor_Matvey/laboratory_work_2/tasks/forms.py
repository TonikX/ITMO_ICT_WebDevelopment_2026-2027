from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import StudentProfile, Work


class SignUpForm(UserCreationForm):
    study_group = forms.CharField(
        label='Учебная группа',
        max_length=60,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'например, K3339'}),
    )

    class Meta:
        model = User
        fields = ('username', 'study_group', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'autofocus': True})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].help_text = 'Логин для входа.'
        self.fields['password1'].help_text = 'Минимум 8 символов, не слишком простой.'
        self.fields['password2'].help_text = 'Повторите пароль.'

    def save(self, commit=True):
        user = super().save(commit=commit)
        StudentProfile.objects.update_or_create(
            user=user,
            defaults={'study_group': self.cleaned_data.get('study_group', '')},
        )
        return user


class WorkForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = ('body',)
        labels = {'body': 'Решение'}
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 7,
                'placeholder': 'Напишите решение здесь...',
            }),
        }
