from django import forms

from .models import ConferenceReview, TalkSubmission


class ConferenceReviewForm(forms.ModelForm):
    class Meta:
        model = ConferenceReview
        fields = ("review_text", "rating")
        widgets = {
            "review_text": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Поделитесь впечатлениями"}
            ),
            "rating": forms.NumberInput(attrs={"min": 1, "max": 10}),
        }


class TalkSubmissionForm(forms.ModelForm):
    class Meta:
        model = TalkSubmission
        fields = ("title", "abstract")
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Название доклада", "maxlength": 200}
            ),
            "abstract": forms.Textarea(
                attrs={
                    "rows": 7,
                    "placeholder": "Расскажите о теме, цели и основных результатах доклада",
                }
            ),
        }
