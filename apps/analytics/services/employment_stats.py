"""Employment outcome aggregation — read-only, computed fresh on every
call. Deliberately never surfaces individual salary or evidence here —
those stay behind Django Admin for admin/management review (see
apps.employment.admin), never as part of an aggregate report, per the
Phase 16 planning decision that salary must only ever appear bucketed
and only in an aggregate context.
"""
from apps.employment.models import EmploymentOutcome

EMPLOYED_STATUSES = {
    EmploymentOutcome.Status.EMPLOYED_FULL_TIME,
    EmploymentOutcome.Status.EMPLOYED_PART_TIME,
    EmploymentOutcome.Status.BUSINESS_OWNER,
    EmploymentOutcome.Status.FREELANCING,
    EmploymentOutcome.Status.PROMOTED,
}


def _latest_outcome_per_student():
    """One row per student who has ever submitted an update — their
    most recent one. Deliberately avoids Postgres-only `.distinct(field)`
    since this project also runs on SQLite (dev/tests) — a plain
    per-student loop is the portable equivalent, and this is an
    admin-reporting view, not a hot path."""
    student_ids = EmploymentOutcome.objects.values_list("student_id", flat=True).distinct()
    outcomes = []
    for student_id in student_ids:
        latest = EmploymentOutcome.objects.filter(student_id=student_id).order_by("-created_at").first()
        if latest:
            outcomes.append(latest)
    return outcomes


def get_employment_summary():
    latest_outcomes = _latest_outcome_per_student()
    total_reporting = len(latest_outcomes)

    status_counts = {choice.value: 0 for choice in EmploymentOutcome.Status}
    for outcome in latest_outcomes:
        status_counts[outcome.status] += 1

    status_breakdown = [
        {"label": label, "count": status_counts[value]}
        for value, label in EmploymentOutcome.Status.choices
    ]

    employed_count = sum(count for status, count in status_counts.items() if status in EMPLOYED_STATUSES)
    employment_rate = round((employed_count / total_reporting) * 100, 1) if total_reporting else 0

    return {
        "total_reporting": total_reporting,
        "employed_count": employed_count,
        "employment_rate": employment_rate,
        "status_breakdown": status_breakdown,
    }
