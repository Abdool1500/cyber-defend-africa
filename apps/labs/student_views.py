from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.permissions import student_required
from apps.enrollments.models import Enrollment

from .models import LabProgress, PracticalLab


def _enrolled_course_ids(student):
    return list(
        Enrollment.objects.filter(student=student, status=Enrollment.Status.ACTIVE).values_list("course_id", flat=True)
    )


@student_required
def lab_list(request):
    course_ids = _enrolled_course_ids(request.user)
    labs = PracticalLab.objects.filter(
        course_id__in=course_ids, status=PracticalLab.Status.PUBLISHED
    ).select_related("course")
    progress_by_lab = {
        p.lab_id: p for p in LabProgress.objects.filter(student=request.user, lab__in=labs)
    }
    rows = [(lab, progress_by_lab.get(lab.id)) for lab in labs]
    return render(request, "student/labs/list.html", {"rows": rows})


@student_required
def lab_detail(request, lab_id):
    course_ids = _enrolled_course_ids(request.user)
    lab = get_object_or_404(PracticalLab, id=lab_id, course_id__in=course_ids, status=PracticalLab.Status.PUBLISHED)
    progress = LabProgress.objects.filter(lab=lab, student=request.user).first()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "start" and progress is None:
            progress = LabProgress.objects.create(lab=lab, student=request.user)
            messages.success(request, "Lab started — good luck!")
        elif action == "complete" and progress is not None and progress.status == LabProgress.Status.IN_PROGRESS:
            progress.status = LabProgress.Status.COMPLETED
            progress.completed_at = timezone.now()
            progress.save(update_fields=["status", "completed_at"])
            messages.success(request, "Lab marked complete — your instructor will review it.")
        elif (
            action == "restart"
            and progress is not None
            and lab.allow_resubmission
            and not progress.is_graded
        ):
            progress.status = LabProgress.Status.IN_PROGRESS
            progress.completed_at = None
            progress.attempts += 1
            progress.save(update_fields=["status", "completed_at", "attempts"])
            messages.success(request, "Lab restarted.")
        return redirect("student_labs:detail", lab_id=lab.id)

    return render(request, "student/labs/detail.html", {"lab": lab, "progress": progress})
