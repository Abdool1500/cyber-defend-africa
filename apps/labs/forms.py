from django import forms

from apps.core.forms import BootstrapFormMixin

from .models import PracticalLab


class PracticalLabForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PracticalLab
        fields = [
            "course", "module", "title", "description", "instructions", "category",
            "max_score", "status", "allow_resubmission",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "instructions": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, instructor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if instructor is not None:
            from apps.instructors.models import InstructorAssignment

            assigned_course_ids = InstructorAssignment.objects.filter(
                instructor=instructor, status=InstructorAssignment.Status.ACTIVE
            ).values_list("course_id", flat=True)
            self.fields["course"].queryset = self.fields["course"].queryset.filter(id__in=assigned_course_ids)


class LabGradeForm(BootstrapFormMixin, forms.Form):
    score = forms.FloatField(min_value=0, required=True)
    instructor_feedback = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    def __init__(self, *args, max_score=None, **kwargs):
        self.max_score = max_score
        super().__init__(*args, **kwargs)

    def clean_score(self):
        score = self.cleaned_data["score"]
        if self.max_score is not None and score > self.max_score:
            raise forms.ValidationError(f"Score cannot exceed the maximum of {self.max_score} points.")
        return score
