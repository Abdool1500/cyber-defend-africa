import csv

from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import render

from apps.accounts.permissions import instructor_required
from apps.analytics.services.nps import calculate_nps
from apps.instructors.models import InstructorAssignment

from .models import StudentFeedback


def _assigned_course_ids(instructor):
    return list(
        InstructorAssignment.objects.filter(
            instructor=instructor, status=InstructorAssignment.Status.ACTIVE
        ).values_list("course_id", flat=True)
    )


def _visible_feedback(instructor):
    """Feedback for this instructor's assigned courses only — an
    instructor must never see feedback tied to a course they aren't
    assigned to, and this is the single query every view below reuses so
    that guarantee lives in one place."""
    return StudentFeedback.objects.filter(course_id__in=_assigned_course_ids(instructor)).select_related(
        "course", "student"
    )


@instructor_required
def feedback_list(request):
    feedback_qs = _visible_feedback(request.user)
    course_filter = request.GET.get("course")
    if course_filter:
        feedback_qs = feedback_qs.filter(course_id=course_filter)

    rows = [
        {
            "id": f.id,
            "course": f.course.title,
            "display_name": f.display_name(),
            "overall_rating": f.overall_rating,
            "content_quality": f.content_quality,
            "practical_lab_quality": f.practical_lab_quality,
            "platform_experience": f.platform_experience,
            "nps_score": f.nps_score,
            "most_helpful": f.most_helpful,
            "improvement_suggestions": f.improvement_suggestions,
            "created_at": f.created_at,
        }
        for f in feedback_qs
    ]

    assigned_courses = InstructorAssignment.objects.filter(
        instructor=request.user, status=InstructorAssignment.Status.ACTIVE
    ).select_related("course")

    return render(request, "instructor/feedback/list.html", {"rows": rows, "assigned_courses": assigned_courses})


@instructor_required
def feedback_analytics(request):
    feedback_qs = _visible_feedback(request.user)
    summary = feedback_qs.aggregate(
        avg_overall=Avg("overall_rating"),
        avg_content=Avg("content_quality"),
        avg_instructor=Avg("instructor_effectiveness"),
        avg_lab=Avg("practical_lab_quality"),
        avg_platform=Avg("platform_experience"),
        avg_difficulty=Avg("difficulty"),
        avg_confidence_before=Avg("confidence_before"),
        avg_confidence_after=Avg("confidence_after"),
    )
    nps = calculate_nps(feedback_qs)

    per_course = feedback_qs.values("course__title").annotate(
        avg_overall=Avg("overall_rating"), responses=Count("id")
    )
    return render(
        request,
        "instructor/feedback/analytics.html",
        {"summary": summary, "nps": nps, "per_course": per_course},
    )


@instructor_required
def feedback_export_csv(request):
    feedback_qs = _visible_feedback(request.user)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="feedback_export.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "Course", "Respondent", "Overall Rating", "Content Quality", "Lab Quality",
        "Platform Experience", "Difficulty", "Confidence Before", "Confidence After",
        "NPS Score", "Most Helpful", "Improvement Suggestions", "Submitted",
    ])
    for f in feedback_qs:
        writer.writerow([
            f.course.title, f.display_name(), f.overall_rating, f.content_quality,
            f.practical_lab_quality, f.platform_experience, f.difficulty,
            f.confidence_before, f.confidence_after, f.nps_score, f.most_helpful,
            f.improvement_suggestions, f.created_at.strftime("%Y-%m-%d"),
        ])
    return response


@instructor_required
def feedback_export_pdf(request):
    from apps.reports.services.pdf import build_feedback_report_pdf

    feedback_qs = _visible_feedback(request.user)
    pdf_bytes = build_feedback_report_pdf(feedback_qs, generated_for=request.user)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="feedback_report.pdf"'
    return response
