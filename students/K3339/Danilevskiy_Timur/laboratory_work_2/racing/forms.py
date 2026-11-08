from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Driver, Entry, Comment, Heat


class SignupForm(UserCreationForm):
    full_name = forms.CharField(label='Фамилия, имя и отчество', max_length=150)
    class Meta:
        model = User
        fields = ['full_name', 'username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['full_name'][:150]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    pass


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['full_name', 'team', 'car', 'bio', 'experience', 'racing_class']
        widgets = {'bio': forms.Textarea(attrs={'rows': 3})}


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['number']

    def __init__(self, *args, race, **kwargs):
        super().__init__(*args, **kwargs)
        self.race = race

    def clean_number(self):
        n = self.cleaned_data['number']
        if Entry.objects.filter(race=self.race, number=n).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Этот номер уже занят. Выберите другой.')
        return n


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['date_from', 'date_to', 'kind', 'rating', 'text']
        widgets = {'date_from': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
                   'date_to': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
                   'text': forms.Textarea(attrs={'rows': 4}),
                   'rating': forms.Select(choices=[(i, f'{i} / 10') for i in range(10, 0, -1)])}


class HeatForm(forms.ModelForm):
    class Meta:
        model = Heat
        fields = ['entry', 'attempt', 'started_at', 'duration', 'position', 'status', 'note']
        widgets = {'started_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')}

    def __init__(self, *args, race, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entry'].queryset = race.entries.select_related('driver', 'race')
        self.fields['started_at'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S']
