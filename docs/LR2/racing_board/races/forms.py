from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, DriverProfile, Registration, Comment


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='Имя', max_length=150)
    last_name = forms.CharField(label='Фамилия', max_length=150)
    email = forms.EmailField(label='Электронная почта')
    phone = forms.CharField(label='Телефон', max_length=20, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']

        if commit:
            user.save()
            DriverProfile.objects.get_or_create(user=user)

        return user


class RaceRegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = []


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_type', 'text', 'rating']
        labels = {
            'comment_type': 'Тип комментария',
            'text': 'Текст комментария',
            'rating': 'Оценка от 1 до 10',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Напишите ваш отзыв о гонке...',
            }),
            'comment_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name not in ('text', 'comment_type', 'rating'):
                field.widget.attrs['class'] = 'form-control'