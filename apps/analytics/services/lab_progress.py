"""Practical-lab progress aggregation, read-only — see
apps.labs for the underlying PracticalLab/LabProgress models."""
from apps.enrollments.models import Enrollment
from apps.labs.models import LabProgress, PracticalLab


def get_lab_summary(student):
    """Not-started/in-progress/completed counts across a student's
    enrolled courses. "Not started" is derived (total published labs
    minus the ones with any progress row), matching how LabProgress
    itself represents "not started" as the absence of a row."""
    course_ids = Enrollment.objects.filter(
        student=student, status=Enrollment.Status.ACTIVE
    ).values_list("course_id", flat=True)

    total_labs = PracticalLab.objects.filter(
        course_id__in=course_ids, status=PracticalLab.Status.PUBLISHED
    ).count()

    progress_qs = LabProgress.objects.filter(
        student=student, lab__course_id__in=course_ids, lab__status=PracticalLab.Status.PUBLISHED,
    )
    completed = progress_qs.filter(status=LabProgress.Status.COMPLETED).count()
    in_progress = progress_qs.filter(status=LabProgress.Status.IN_PROGRESS).count()

    return {
        "total": total_labs,
        "completed": completed,
        "in_progress": in_progress,
        "not_started": max(total_labs - completed - in_progress, 0),
    }
