"""Learning-time aggregation, read-only — computed fresh from
LearningTimeEntry on every call (same "never cache, always derive"
philosophy as apps.analytics.services.skill_improvement), so it can
never drift out of sync with the underlying heartbeat data.
"""
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from ..models import LearningTimeEntry

LESSON_TYPES = ["video", "reading", "lab", "live"]


def _sum_seconds(queryset):
    return queryset.aggregate(total=Sum("seconds"))["total"] or 0


def get_learning_time_summary(student):
    """Today/this-week/this-month/lifetime totals, all in seconds."""
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    entries = LearningTimeEntry.objects.filter(student=student)
    return {
        "today_seconds": _sum_seconds(entries.filter(date=today)),
        "week_seconds": _sum_seconds(entries.filter(date__gte=week_start)),
        "month_seconds": _sum_seconds(entries.filter(date__gte=month_start)),
        "lifetime_seconds": _sum_seconds(entries),
    }


def get_course_time_breakdown(student, course):
    """Lifetime time spent in this course, split by lesson content type
    (video/reading/lab/live)."""
    entries = LearningTimeEntry.objects.filter(student=student, lesson__module__course=course)
    by_type = entries.values("lesson__lesson_type").annotate(total=Sum("seconds"))
    breakdown = dict.fromkeys(LESSON_TYPES, 0)
    for row in by_type:
        lesson_type = row["lesson__lesson_type"]
        if lesson_type in breakdown:
            breakdown[lesson_type] = row["total"] or 0
    return {"total_seconds": sum(breakdown.values()), "by_type": breakdown}


def get_learning_streak(student):
    """Consecutive days (ending today or yesterday) with at least one
    LearningTimeEntry. A streak "survives" a day that hasn't happened
    yet — i.e. no entry for today doesn't break a streak that was still
    active as of yesterday — so a student checking the dashboard first
    thing in the morning doesn't see their streak reset before they've
    had a chance to study today."""
    active_dates = set(
        LearningTimeEntry.objects.filter(student=student).values_list("date", flat=True)
    )
    if not active_dates:
        return {"current_streak": 0}

    today = timezone.localdate()
    cursor = today if today in active_dates else today - timedelta(days=1)
    if cursor not in active_dates:
        return {"current_streak": 0}

    streak = 0
    while cursor in active_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return {"current_streak": streak}
