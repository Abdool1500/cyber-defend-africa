from django import forms

from apps.core.forms import BootstrapFormMixin

from .models import StudentFeedback

RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
OPTIONAL_RATING_CHOICES = [("", "Not applicable")] + RATING_CHOICES
NPS_CHOICES = [(i, str(i)) for i in range(0, 11)]


class StudentFeedbackForm(BootstrapFormMixin, forms.ModelForm):
    overall_rating = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int, label="Course satisfaction")
    content_quality = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int)
    instructor_effectiveness = forms.TypedChoiceField(
        choices=OPTIONAL_RATING_CHOICES, coerce=int, required=False, empty_value=None, label="Instructor rating",
    )
    practical_lab_quality = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int, label="Lab quality")
    platform_experience = forms.TypedChoiceField(choices=RATING_CHOICES, coerce=int)
    difficulty = forms.TypedChoiceField(
        choices=RATING_CHOICES, coerce=int, label="Difficulty", help_text="1 = Very Easy, 5 = Very Difficult",
    )
    confidence_before = forms.TypedChoiceField(
        choices=RATING_CHOICES, coerce=int, label="Confidence before this course",
        help_text="1 = Not at all confident, 5 = Very confident",
    )
    confidence_after = forms.TypedChoiceField(
        choices=RATING_CHOICES, coerce=int, label="Confidence after this course",
        help_text="1 = Not at all confident, 5 = Very confident",
    )
    nps_score = forms.TypedChoiceField(
        choices=NPS_CHOICES, coerce=int, label="How likely are you to recommend this course to a friend or colleague?",
        help_text="0 = Not at all likely, 10 = Extremely likely",
    )

    class Meta:
        model = StudentFeedback
        fields = [
            "overall_rating", "content_quality", "instructor_effectiveness", "practical_lab_quality",
            "platform_experience", "difficulty", "confidence_before", "confidence_after", "nps_score",
            "most_helpful", "improvement_suggestions", "additional_comments", "is_anonymous",
        ]
        widgets = {
            "most_helpful": forms.Textarea(attrs={"rows": 2}),
            "improvement_suggestions": forms.Textarea(attrs={"rows": 2}),
            "additional_comments": forms.Textarea(attrs={"rows": 2}),
        }
