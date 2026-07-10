from django import forms
from django.forms import inlineformset_factory

from apps.core.forms import BootstrapFormMixin

from .models import Question, QuestionOption


class QuestionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            "course", "module", "topic", "question_type", "question_text",
            "difficulty", "default_points", "explanation", "model_answer",
            "grading_guidance", "status",
        ]
        widgets = {
            "question_text": forms.Textarea(attrs={"rows": 3}),
            "explanation": forms.Textarea(attrs={"rows": 2}),
            "model_answer": forms.Textarea(attrs={"rows": 2}),
            "grading_guidance": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, instructor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if instructor is not None:
            from apps.instructors.models import InstructorAssignment

            assigned_course_ids = InstructorAssignment.objects.filter(
                instructor=instructor, status=InstructorAssignment.Status.ACTIVE
            ).values_list("course_id", flat=True)
            self.fields["course"].queryset = self.fields["course"].queryset.filter(id__in=assigned_course_ids)
        # Note: UUID primary keys get a default value at instantiation time
        # (unlike auto-increment ids), so `self.instance.pk` is never a
        # reliable "is this saved?" check here — course_id is, since it has
        # no default and is only set once a course is actually chosen.
        if self.instance.course_id:
            self.fields["module"].queryset = self.fields["module"].queryset.filter(course_id=self.instance.course_id)


class QuestionOptionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = QuestionOption
        fields = ["option_text", "is_correct", "display_order"]


QuestionOptionFormSet = inlineformset_factory(
    Question,
    QuestionOption,
    form=QuestionOptionForm,
    extra=4,
    min_num=2,
    validate_min=True,
    can_delete=True,
)


def validate_options_for_type(question_type, formset):
    """Server-side re-validation of option correctness by question type —
    the JS-driven dynamic editor is UX only, this is the real guard."""
    cleaned_forms = [
        f for f in formset.forms
        if f.cleaned_data and not f.cleaned_data.get("DELETE", False) and f.cleaned_data.get("option_text")
    ]
    if question_type in (Question.QuestionType.MULTIPLE_CHOICE, Question.QuestionType.TRUE_FALSE):
        correct_count = sum(1 for f in cleaned_forms if f.cleaned_data.get("is_correct"))
        if len(cleaned_forms) < 2:
            raise forms.ValidationError("Provide at least two options.")
        if correct_count != 1:
            raise forms.ValidationError("Exactly one option must be marked correct.")
    elif question_type == Question.QuestionType.MULTIPLE_SELECT:
        correct_count = sum(1 for f in cleaned_forms if f.cleaned_data.get("is_correct"))
        if len(cleaned_forms) < 2:
            raise forms.ValidationError("Provide at least two options.")
        if correct_count < 1:
            raise forms.ValidationError("At least one option must be marked correct.")
    return cleaned_forms
