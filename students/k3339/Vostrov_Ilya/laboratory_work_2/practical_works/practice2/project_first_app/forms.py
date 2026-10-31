"""Формы приложения "Автовладельцы" (Практическое занятие 2).

Задание 3: собственная форма владельца на основе ModelForm (FBV).
Формы для автомобиля (создание/обновление/удаление) строятся самими
CBV-представлениями через их атрибуты fields/success_url.
"""

from django import forms

from .models import Owner


class OwnerForm(forms.ModelForm):
    """Форма ввода владельца: имя, фамилия, дата рождения."""

    class Meta:
        model = Owner
        fields = ['first_name', 'last_name', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
