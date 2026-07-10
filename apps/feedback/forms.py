from django import forms

from apps.core.forms import BootstrapFormMixin

from .models import StudentFeedback

RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
OPTIONAL_RATING_CHOICES = [("", "Not applicable")] + RATING_CHOICES


class StudentFeedbackForm(BootstrapFormMixin, forms.ModelForm):
    overall_rating = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int)
    content_quality = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int)
    instructor_effectiveness = forms.TypedChoiceField(
        choices=OPTIONAL_RATING_CHOICES, coerce=int, required=False, empty_value=None
    )
    practical_lab_quality = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int)
    platform_experience = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int)

    class Meta:
        model = StudentFeedback
        fields = [
            "overall_rating", "content_quality", "instructor_effectiveness", "practical_lab_quality",
            "platform_experience", "most_helpful", "improvement_suggestions", "additional_comments",
            "is_anonymous",
        ]
        widgets = {
            "most_helpful": forms.Textarea(attrs={"rows": 2}),
            "improvement_suggestions": forms.Textarea(attrs={"rows": 2}),
            "additional_comments": forms.Textarea(attrs={"rows": 2}),
        }
