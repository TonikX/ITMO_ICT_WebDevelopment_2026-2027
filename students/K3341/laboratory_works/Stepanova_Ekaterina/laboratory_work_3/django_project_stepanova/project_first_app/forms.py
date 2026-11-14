from django import forms
from django.contrib.auth import get_user_model



class CarOwnerForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['last_name', 'first_name', 'birthday', 'passport', 'home_address', 'nationality']

