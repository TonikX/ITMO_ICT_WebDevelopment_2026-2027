from django import forms
from .models import Submission

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['answer_text']
        labels = {
            'answer_text': 'Текст ответа'
        }
        widgets = {
            'answer_text': forms.Textarea(attrs={'rows': 8})
        }


class GradeForm(forms.ModelForm):
    grade = forms.IntegerField(
        min_value=1,
        max_value=5,
        label='Оценка'
    )

    class Meta:
        model = Submission
        fields = ['grade']
