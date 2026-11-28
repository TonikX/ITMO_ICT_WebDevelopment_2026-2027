from django import forms
from django.contrib.auth import get_user_model
from .models import CarOwner

User = get_user_model()


class CarOwnerForm(forms.ModelForm):
    class Meta:
        model = CarOwner
        fields = ['first_name', 'last_name', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'passport_number', 'home_address', 'nationality']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user