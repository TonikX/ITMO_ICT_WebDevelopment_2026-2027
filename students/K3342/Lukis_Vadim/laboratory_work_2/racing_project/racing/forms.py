from django import forms
from .models import CarOwner, Car, Ownership
from .models import Race, RaceRegistration, Review
from .models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class CarOwnerForm(forms.ModelForm):
    """Форма для создания/редактирования владельца"""
    class Meta:
        model = CarOwner
        fields = ['first_name', 'last_name', 'birth_date', 'passport_number', 'address']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.Select)):
                field.widget.attrs.setdefault('class', 'form-control')


class CarForm(forms.ModelForm):
    """Форма для создания/редактирования автомобиля"""
    class Meta:
        model = Car
        fields = ['license_plate', 'brand', 'model', 'color', 'year']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 1900, 'max': 2026}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.Select)):
                field.widget.attrs.setdefault('class', 'form-control')


class OwnershipForm(forms.ModelForm):
    """Форма для создания/редактирования владения"""
    class Meta:
        model = Ownership
        fields = ['car_owner', 'car', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.Select)):
                field.widget.attrs.setdefault('class', 'form-control')


class RaceForm(forms.ModelForm):
    """Форма для создания/редактирования гонки"""
    class Meta:
        model = Race
        fields = ['name', 'race_date', 'track_location', 'description']
        widgets = {
            'race_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.Select)):
                field.widget.attrs.setdefault('class', 'form-control')


class RaceRegistrationForm(forms.ModelForm):
    """Форма регистрации на гонку"""
    class Meta:
        model = RaceRegistration
        fields = ['racer', 'race']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.Select)):
                field.widget.attrs.setdefault('class', 'form-control')


class ReviewForm(forms.ModelForm):
    """Форма для создания отзыва"""
    class Meta:
        model = Review
        fields = ['comment_text', 'comment_type', 'rating']
        widgets = {
            'comment_text': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect, forms.Select)):
                field.widget.attrs.setdefault('class', 'form-control')


from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации нового пользователя"""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class CustomAuthenticationForm(AuthenticationForm):
    """Форма входа"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
