from django import forms

from .models import Conference, Registration, Review


class ConferenceForm(forms.ModelForm):
    class Meta:
        model = Conference
        fields = [
            'title', 'topics', 'venue_name', 'venue_description',
            'start_date', 'end_date', 'description', 'participation_terms',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'venue_description': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'participation_terms': forms.Textarea(attrs={'rows': 3}),
            'topics': forms.CheckboxSelectMultiple,
        }


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['talk_title']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {'text': forms.Textarea(attrs={'rows': 3})}
