from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.permissions import instructor_required
from apps.core.services.storage import StorageError, get_storage_service
from apps.instructors.models import InstructorAssignment

from .forms import AssignmentForm, GradeSubmissionForm
from .models import Assignment, AssignmentSubmission


def _assigned_course_ids(instructor):
    return list(
        InstructorAssignment.objects.filter(
            instructor=instructor, status=InstructorAssignment.Status.ACTIVE
        ).values_list("course_id", flat=True)
    )


def _get_owned_assignment(instructor, assignment_id):
    return get_object_or_404(Assignment, id=assignment_id, course_id__in=_assigned_course_ids(instructor))


@instructor_required
def assignment_list(request):
    assignments = Assignment.objects.filter(course_id__in=_assigned_course_ids(request.user)).select_related("course")
    return render(request, "instructor/assignments/list.html", {"assignments": assignments})


@instructor_required
def assignment_create(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST, instructor=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, "Assignment created.")
            return redirect("instructor_assignments:list")
    else:
        form = AssignmentForm(instructor=request.user)
    return render(request, "instructor/assignments/form.html", {"form": form, "is_edit": False})


@instructor_required
def assignment_edit(request, assignment_id):
    assignment = _get_owned_assignment(request.user, assignment_id)
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment, instructor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated.")
            return redirect("instructor_assignments:list")
    else:
        form = AssignmentForm(instance=assignment, instructor=request.user)
    return render(request, "instructor/assignments/form.html", {"form": form, "is_edit": True, "assignment": assignment})


@instructor_required
def submission_list(request, assignment_id):
    assignment = _get_owned_assignment(request.user, assignment_id)
    submissions = assignment.submissions.select_related("student").order_by("-submitted_at")
    return render(request, "instructor/assignments/submissions.html", {"assignment": assignment, "submissions": submissions})


@instructor_required
def submission_grade(request, assignment_id, submission_id):
    assignment = _get_owned_assignment(request.user, assignment_id)
    submission = get_object_or_404(AssignmentSubmission, id=submission_id, assignment=assignment)

    signed_url = None
    if submission.storage_path:
        try:
            signed_url = get_storage_service().signed_url("assignment-submissions", submission.storage_path)
        except StorageError:
            signed_url = None

    if request.method == "POST":
        form = GradeSubmissionForm(request.POST, max_points=assignment.max_points)
        if form.is_valid():
            submission.score = form.cleaned_data["score"]
            submission.instructor_feedback = form.cleaned_data["instructor_feedback"]
            submission.graded_by = request.user
            submission.graded_at = timezone.now()
            submission.status = AssignmentSubmission.Status.GRADED
            submission.save()
            from apps.audit.services import log_action

            log_action(request.user, "assignment_submission.grade", submission, {"score": submission.score})
            messages.success(request, "Submission graded.")
            return redirect("instructor_assignments:submissions", assignment_id=assignment.id)
    else:
        form = GradeSubmissionForm(
            initial={"score": submission.score, "instructor_feedback": submission.instructor_feedback},
            max_points=assignment.max_points,
        )

    return render(request, "instructor/assignments/grade.html", {
        "assignment": assignment, "submission": submission, "form": form, "signed_url": signed_url,
    })
