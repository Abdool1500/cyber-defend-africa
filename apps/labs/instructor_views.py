from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.permissions import instructor_required
from apps.audit.services import log_action
from apps.instructors.models import InstructorAssignment

from .forms import LabGradeForm, PracticalLabForm
from .models import LabProgress, PracticalLab


def _assigned_course_ids(instructor):
    return list(
        InstructorAssignment.objects.filter(
            instructor=instructor, status=InstructorAssignment.Status.ACTIVE
        ).values_list("course_id", flat=True)
    )


def _get_owned_lab(instructor, lab_id):
    return get_object_or_404(PracticalLab, id=lab_id, course_id__in=_assigned_course_ids(instructor))


@instructor_required
def lab_list(request):
    labs = PracticalLab.objects.filter(course_id__in=_assigned_course_ids(request.user)).select_related("course")
    return render(request, "instructor/labs/list.html", {"labs": labs})


@instructor_required
def lab_create(request):
    if request.method == "POST":
        form = PracticalLabForm(request.POST, instructor=request.user)
        if form.is_valid():
            lab = form.save(commit=False)
            lab.created_by = request.user
            lab.save()
            messages.success(request, "Lab created.")
            return redirect("instructor_labs:list")
    else:
        form = PracticalLabForm(instructor=request.user)
    return render(request, "instructor/labs/form.html", {"form": form, "is_edit": False})


@instructor_required
def lab_edit(request, lab_id):
    lab = _get_owned_lab(request.user, lab_id)
    if request.method == "POST":
        form = PracticalLabForm(request.POST, instance=lab, instructor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Lab updated.")
            return redirect("instructor_labs:list")
    else:
        form = PracticalLabForm(instance=lab, instructor=request.user)
    return render(request, "instructor/labs/form.html", {"form": form, "is_edit": True, "lab": lab})


@instructor_required
def lab_progress_list(request, lab_id):
    lab = _get_owned_lab(request.user, lab_id)
    progress_records = lab.progress_records.select_related("student").order_by("-started_at")
    return render(request, "instructor/labs/progress_list.html", {"lab": lab, "progress_records": progress_records})


@instructor_required
def lab_grade(request, lab_id, progress_id):
    lab = _get_owned_lab(request.user, lab_id)
    progress = get_object_or_404(LabProgress, id=progress_id, lab=lab)

    if request.method == "POST":
        form = LabGradeForm(request.POST, max_score=lab.max_score)
        if form.is_valid():
            progress.score = form.cleaned_data["score"]
            progress.instructor_feedback = form.cleaned_data["instructor_feedback"]
            progress.graded_by = request.user
            progress.graded_at = timezone.now()
            progress.save(update_fields=["score", "instructor_feedback", "graded_by", "graded_at"])
            log_action(request.user, "lab_progress.grade", progress, {"score": progress.score})
            messages.success(request, "Lab graded.")
            return redirect("instructor_labs:progress_list", lab_id=lab.id)
    else:
        form = LabGradeForm(
            initial={"score": progress.score, "instructor_feedback": progress.instructor_feedback},
            max_score=lab.max_score,
        )

    return render(request, "instructor/labs/grade.html", {"lab": lab, "progress": progress, "form": form})
