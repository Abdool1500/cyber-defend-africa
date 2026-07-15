from django import forms

from apps.core.forms import BootstrapFormMixin

from .models import Quiz, QuizRandomRule


class QuizForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Quiz
        fields = [
            "course", "module", "title", "description", "instructions", "status", "quiz_type",
            "time_limit_minutes", "attempt_limit", "passing_score",
            "shuffle_questions", "shuffle_options",
            "show_score_after_submission", "show_correct_answers", "show_explanations",
            "available_from", "available_until",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "instructions": forms.Textarea(attrs={"rows": 3}),
            "available_from": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "available_until": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, instructor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if instructor is not None:
            from apps.instructors.models import InstructorAssignment

            assigned_course_ids = InstructorAssignment.objects.filter(
                instructor=instructor, status=InstructorAssignment.Status.ACTIVE
            ).values_list("course_id", flat=True)
            self.fields["course"].queryset = self.fields["course"].queryset.filter(id__in=assigned_course_ids)


class QuizRandomRuleForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = QuizRandomRule
        fields = ["difficulty", "topic", "question_type", "number_of_questions"]
