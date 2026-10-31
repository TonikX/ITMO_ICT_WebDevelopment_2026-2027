from django import forms
from django.contrib.auth.models import User
from .models import CarOwner, UserProfile


class CarOwnerForm(forms.ModelForm):
    class Meta:
        model = CarOwner
        fields = ['surname', 'name', 'birth_date']


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Пароль'
    )

    passport_number = forms.CharField(label='Номер паспорта')
    home_address = forms.CharField(label='Домашний адрес')
    nationality = forms.CharField(label='Национальность')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            UserProfile.objects.create(
                user=user,
                passport_number=self.cleaned_data['passport_number'],
                home_address=self.cleaned_data['home_address'],
                nationality=self.cleaned_data['nationality']
            )

        return user