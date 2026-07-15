from django import forms
from django.utils import timezone

from apps.core.forms import BootstrapFormMixin
from apps.core.services import storage

from .models import EmploymentOutcome


class EmploymentOutcomeForm(BootstrapFormMixin, forms.ModelForm):
    evidence = forms.FileField(
        required=False, label="Supporting evidence",
        help_text="Optional — offer letter, contract, or similar. PDF, DOC, or image. Max 20 MB.",
    )

    class Meta:
        model = EmploymentOutcome
        fields = [
            "status", "employer", "job_title", "country", "date_employed",
            "salary_range", "how_academy_helped",
        ]
        widgets = {
            "date_employed": forms.DateInput(attrs={"type": "date"}),
            "how_academy_helped": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_evidence(self):
        evidence = self.cleaned_data.get("evidence")
        if evidence:
            try:
                content_type = evidence.content_type or "application/octet-stream"
                storage.validate_mime_type(content_type)
                storage.validate_file_size(evidence.size)
            except storage.InvalidFileError as exc:
                raise forms.ValidationError(str(exc))
        return evidence

    def clean_date_employed(self):
        date_employed = self.cleaned_data.get("date_employed")
        if date_employed and date_employed > timezone.now().date():
            raise forms.ValidationError("Date employed cannot be in the future.")
        return date_employed
