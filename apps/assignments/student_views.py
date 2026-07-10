from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.permissions import student_required
from apps.core.services.storage import StorageError, generate_safe_path, get_storage_service
from apps.enrollments.models import Enrollment

from .forms import SubmissionForm
from .models import Assignment, AssignmentSubmission


def _enrolled_course_ids(student):
    return list(
        Enrollment.objects.filter(student=student, status=Enrollment.Status.ACTIVE).values_list("course_id", flat=True)
    )


@student_required
def assignment_list(request):
    course_ids = _enrolled_course_ids(request.user)
    assignments = Assignment.objects.filter(
        course_id__in=course_ids, status=Assignment.Status.PUBLISHED
    ).select_related("course")
    existing_by_assignment = {
        s.assignment_id: s
        for s in AssignmentSubmission.objects.filter(student=request.user, assignment__in=assignments)
    }
    rows = [(a, existing_by_assignment.get(a.id)) for a in assignments]
    return render(request, "student/assignments/list.html", {"rows": rows})


@student_required
def assignment_detail(request, assignment_id):
    course_ids = _enrolled_course_ids(request.user)
    assignment = get_object_or_404(
        Assignment, id=assignment_id, course_id__in=course_ids, status=Assignment.Status.PUBLISHED
    )
    submission = AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).first()

    signed_url = None
    if submission and submission.storage_path:
        try:
            signed_url = get_storage_service().signed_url("assignment-submissions", submission.storage_path)
        except StorageError:
            signed_url = None

    can_submit = submission is None or (submission.status != AssignmentSubmission.Status.GRADED and assignment.allow_resubmission)
    is_past_due = assignment.due_at and timezone.now() > assignment.due_at

    if request.method == "POST":
        if not can_submit:
            messages.error(request, "This assignment has already been graded and cannot be resubmitted.")
            return redirect("student_assignments:detail", assignment_id=assignment.id)
        if is_past_due and not assignment.allow_late_submissions:
            messages.error(request, "The deadline for this assignment has passed and late submissions are not accepted.")
            return redirect("student_assignments:detail", assignment_id=assignment.id)

        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            storage_path = submission.storage_path if submission else None
            original_filename = submission.original_filename if submission else None
            attachment = form.cleaned_data.get("attachment")
            if attachment:
                path = generate_safe_path(
                    "assignments", str(assignment.course_id), str(assignment.id), str(request.user.id),
                    original_filename=attachment.name,
                )
                try:
                    get_storage_service().upload(
                        "assignment-submissions", path, attachment, content_type=attachment.content_type
                    )
                    storage_path = path
                    original_filename = attachment.name
                except StorageError as exc:
                    messages.error(request, f"File upload failed: {exc}")
                    return render(request, "student/assignments/detail.html", {
                        "assignment": assignment, "submission": submission, "form": form,
                        "can_submit": can_submit, "is_past_due": is_past_due, "signed_url": signed_url,
                    })

            status = AssignmentSubmission.Status.LATE if is_past_due else AssignmentSubmission.Status.SUBMITTED
            submission, _ = AssignmentSubmission.objects.update_or_create(
                assignment=assignment, student=request.user,
                defaults={
                    "text_submission": form.cleaned_data.get("text_submission", ""),
                    "storage_path": storage_path,
                    "original_filename": original_filename,
                    "status": status,
                },
            )
            messages.success(request, "Your submission has been received.")
            return redirect("student_assignments:detail", assignment_id=assignment.id)
    else:
        form = SubmissionForm(initial={"text_submission": submission.text_submission if submission else ""})

    return render(request, "student/assignments/detail.html", {
        "assignment": assignment, "submission": submission, "form": form,
        "can_submit": can_submit, "is_past_due": is_past_due, "signed_url": signed_url,
    })
