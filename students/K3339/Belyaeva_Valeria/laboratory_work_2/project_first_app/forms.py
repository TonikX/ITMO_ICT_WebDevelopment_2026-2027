from django import forms
from flights.forms import SignupForm


class OwnerForm(SignupForm):
    class Meta(SignupForm.Meta):
        fields = SignupForm.Meta.fields + ['birth_date', 'passport_number', 'home_address', 'nationality']
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}
