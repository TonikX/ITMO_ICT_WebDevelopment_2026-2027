from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Car

User = get_user_model()


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    passport_number = forms.CharField(
        max_length=20, label='Номер паспорта',
        widget=forms.TextInput(attrs={'placeholder': '1234 567890'})
    )
    home_address = forms.CharField(
        max_length=255, label='Домашний адрес',
        widget=forms.TextInput(attrs={'placeholder': 'г. Москва, ул. Ленина, д. 1'})
    )
    nationality = forms.CharField(
        max_length=50, label='Национальность',
        widget=forms.TextInput(attrs={'placeholder': 'Русский'})
    )
    birth_date = forms.DateField(
        required=False,
        label='Дата рождения',
        widget=forms.DateInput(
            attrs={'type': 'text', 'placeholder': 'ДД.ММ.ГГГГ'},
            format='%d.%m.%Y'
        ),
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'passport_number', 'home_address', 'nationality', 'birth_date',
            'password1', 'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['birth_date'].input_formats = ['%d.%m.%Y']


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['state_number', 'brand', 'model', 'color']
        labels = {
            'state_number': 'Гос. номер',
            'brand': 'Марка',
            'model': 'Модель',
            'color': 'Цвет',
        }