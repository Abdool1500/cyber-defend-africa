from django import forms

from apps.core.forms import BootstrapFormMixin
from apps.core.services.storage import MAX_FILE_SIZE_BYTES, ALLOWED_MIME_TYPES

from .models import Assignment


class AssignmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            "course", "module", "title", "description", "instructions",
            "due_at", "max_points", "status", "allow_late_submissions", "allow_resubmission",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "instructions": forms.Textarea(attrs={"rows": 3}),
            "due_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, instructor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if instructor is not None:
            from apps.instructors.models import InstructorAssignment

            assigned_course_ids = InstructorAssignment.objects.filter(
                instructor=instructor, status=InstructorAssignment.Status.ACTIVE
            ).values_list("course_id", flat=True)
            self.fields["course"].queryset = self.fields["course"].queryset.filter(id__in=assigned_course_ids)


class SubmissionForm(BootstrapFormMixin, forms.Form):
    text_submission = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}), required=False)
    attachment = forms.FileField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("text_submission", "").strip()
        attachment = cleaned_data.get("attachment")
        if not text and not attachment:
            raise forms.ValidationError("Provide a text submission and/or a file attachment.")
        if attachment:
            if attachment.size > MAX_FILE_SIZE_BYTES:
                raise forms.ValidationError("The attached file is too large (maximum 20 MB).")
            content_type = attachment.content_type
            if content_type not in ALLOWED_MIME_TYPES:
                raise forms.ValidationError(f"File type '{content_type}' is not permitted.")
        return cleaned_data


class GradeSubmissionForm(BootstrapFormMixin, forms.Form):
    score = forms.FloatField(min_value=0, required=True)
    instructor_feedback = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    def __init__(self, *args, max_points=None, **kwargs):
        self.max_points = max_points
        super().__init__(*args, **kwargs)

    def clean_score(self):
        score = self.cleaned_data["score"]
        if self.max_points is not None and score > self.max_points:
            raise forms.ValidationError(f"Score cannot exceed the maximum of {self.max_points} points.")
        return score
