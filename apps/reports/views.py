import csv

from django.http import HttpResponse
from django.shortcuts import render

from apps.accounts.permissions import admin_required
from apps.analytics.services.employment_stats import get_employment_summary
from apps.analytics.services.fid_report import get_fid_impact_report_data
from apps.analytics.services.impact_stats import get_impact_dashboard_data
from apps.analytics.services.platform_stats import get_platform_analytics
from apps.enrollments.models import Enrollment
from apps.leads.models import ConsultationRequest, ContactSubmission, DemoRequest, PilotRequest

from .services.excel import (
    build_course_report_excel,
    build_employment_report_excel,
    build_fid_impact_report_excel,
    build_impact_report_excel,
    build_student_report_excel,
)
from .services.pdf import (
    build_course_report_pdf,
    build_employment_report_pdf,
    build_fid_impact_report_pdf,
    build_impact_report_pdf,
    build_student_report_pdf,
)
from .services.report_data import get_course_report_rows, get_student_report_rows


@admin_required
def reports_index(request):
    return render(request, "management/reports/index.html")


@admin_required
def analytics_dashboard(request):
    analytics = get_platform_analytics()
    chart_data = {
        "top_courses": {
            "labels": [row["course__title"] for row in analytics["top_courses"]],
            "values": [row["enrollment_count"] for row in analytics["top_courses"]],
        },
        "top_instructors": {
            "labels": [row["instructor__full_name"] for row in analytics["top_instructors"]],
            "values": [round(row["avg_rating"], 1) for row in analytics["top_instructors"]],
        },
        "enrollment_health": {
            "labels": ["Completed", "Dropped Out", "Other"],
            "values": [
                round(analytics["completion_rate"], 1),
                round(analytics["dropout_rate"], 1),
                round(100 - analytics["completion_rate"] - analytics["dropout_rate"], 1),
            ],
        },
        "skill_improvement": {
            "labels": ["Pre-Test", "Post-Test"],
            "values": [analytics["avg_pre_test"] or 0, analytics["avg_post_test"] or 0],
        },
    }
    return render(
        request,
        "management/reports/analytics_dashboard.html",
        {"analytics": analytics, "chart_data": chart_data},
    )


@admin_required
def impact_dashboard(request):
    impact = get_impact_dashboard_data()
    return render(request, "management/reports/impact_dashboard.html", {"impact": impact})


@admin_required
def export_impact_csv(request):
    impact = get_impact_dashboard_data()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="impact_report.csv"'
    writer = csv.writer(response)
    writer.writerow(["Metric", "Value", "Type"])
    computed_labels = {
        "people_trained": "People Trained",
        "certificates_issued": "Certificates Issued",
        "total_learning_hours": "Total Learning Hours",
        "labs_completed": "Labs Completed",
        "completion_rate": "Completion Rate (%)",
        "average_score": "Average Quiz Score (%)",
        "avg_skill_improvement": "Average Skill Improvement (%)",
        "employment_rate": "Employment Rate (%)",
        "nps_score": "Net Promoter Score",
    }
    for key, label in computed_labels.items():
        writer.writerow([label, impact["computed"][key], "Computed"])

    self_reported_labels = {
        "smes_protected": "SMEs Protected",
        "healthcare_workers_trained": "Healthcare Workers Trained",
        "businesses_started": "Businesses Started",
    }
    as_of = impact["self_reported"]["as_of"]
    for key, label in self_reported_labels.items():
        writer.writerow([label, impact["self_reported"][key], "Self-Reported"])
    if as_of:
        writer.writerow(["Self-Reported As Of", as_of.strftime("%Y-%m-%d"), "Self-Reported"])
    return response


@admin_required
def export_impact_excel(request):
    impact = get_impact_dashboard_data()
    response = HttpResponse(
        build_impact_report_excel(impact),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="impact_report.xlsx"'
    return response


@admin_required
def export_impact_pdf(request):
    impact = get_impact_dashboard_data()
    response = HttpResponse(build_impact_report_pdf(impact), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="impact_report.pdf"'
    return response


@admin_required
def export_course_csv(request):
    rows = get_course_report_rows()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="course_report.csv"'
    writer = csv.writer(response)
    writer.writerow(["Course", "Total Enrollments", "Completed", "Completion Rate (%)", "Average Score (%)", "Average Rating", "Certificates Issued"])
    for row in rows:
        writer.writerow([
            row["course_title"], row["total_enrollments"], row["completed_enrollments"],
            row["completion_rate"], row["average_score"], row["average_rating"], row["certificates_issued"],
        ])
    return response


@admin_required
def export_course_excel(request):
    rows = get_course_report_rows()
    response = HttpResponse(
        build_course_report_excel(rows),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="course_report.xlsx"'
    return response


@admin_required
def export_course_pdf(request):
    rows = get_course_report_rows()
    response = HttpResponse(build_course_report_pdf(rows), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="course_report.pdf"'
    return response


@admin_required
def export_student_csv(request):
    rows = get_student_report_rows()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="student_report.csv"'
    writer = csv.writer(response)
    writer.writerow(["Student", "Email", "Total Enrollments", "Completed", "Average Score (%)", "Certificates Earned", "Learning Hours"])
    for row in rows:
        writer.writerow([
            row["student_name"], row["student_email"], row["total_enrollments"], row["completed_enrollments"],
            row["average_score"], row["certificates_earned"], row["learning_hours"],
        ])
    return response


@admin_required
def export_student_excel(request):
    rows = get_student_report_rows()
    response = HttpResponse(
        build_student_report_excel(rows),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="student_report.xlsx"'
    return response


@admin_required
def export_student_pdf(request):
    rows = get_student_report_rows()
    response = HttpResponse(build_student_report_pdf(rows), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="student_report.pdf"'
    return response


@admin_required
def export_employment_csv(request):
    employment = get_employment_summary()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="employment_report.csv"'
    writer = csv.writer(response)
    writer.writerow(["Status", "Count"])
    for row in employment["status_breakdown"]:
        writer.writerow([row["label"], row["count"]])
    writer.writerow(["Total Reporting", employment["total_reporting"]])
    writer.writerow(["Employment Rate (%)", employment["employment_rate"]])
    return response


@admin_required
def export_employment_excel(request):
    employment = get_employment_summary()
    response = HttpResponse(
        build_employment_report_excel(employment),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="employment_report.xlsx"'
    return response


@admin_required
def export_employment_pdf(request):
    employment = get_employment_summary()
    response = HttpResponse(build_employment_report_pdf(employment), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="employment_report.pdf"'
    return response


@admin_required
def export_fid_pdf(request):
    data = get_fid_impact_report_data(prepared_for=request.GET.get("prepared_for") or None)
    response = HttpResponse(build_fid_impact_report_pdf(data), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="fid_impact_evidence_report.pdf"'
    return response


@admin_required
def export_fid_excel(request):
    data = get_fid_impact_report_data(prepared_for=request.GET.get("prepared_for") or None)
    response = HttpResponse(
        build_fid_impact_report_excel(data),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="fid_impact_evidence_report.xlsx"'
    return response


@admin_required
def export_enrollments_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="enrollments_report.csv"'
    writer = csv.writer(response)
    writer.writerow(["Student", "Course", "Status", "Progress %", "Enrolled At"])
    for e in Enrollment.objects.select_related("student", "course"):
        writer.writerow([e.student.email, e.course.title, e.status, e.progress_percentage, e.enrolled_at.strftime("%Y-%m-%d")])
    return response


@admin_required
def export_leads_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="leads_report.csv"'
    writer = csv.writer(response)
    writer.writerow(["Type", "Name", "Email", "Organization", "Status/Inquiry", "Created At"])
    for c in ContactSubmission.objects.all():
        writer.writerow(["Contact", c.full_name, c.email, c.organization or "", c.inquiry_type, c.created_at.strftime("%Y-%m-%d")])
    for d in DemoRequest.objects.all():
        writer.writerow(["Demo Request", d.full_name, d.work_email, d.organization, d.status, d.created_at.strftime("%Y-%m-%d")])
    for p in PilotRequest.objects.all():
        writer.writerow(["Pilot Request", p.full_name, p.work_email, p.organization, p.status, p.created_at.strftime("%Y-%m-%d")])
    for cr in ConsultationRequest.objects.all():
        writer.writerow(["Consultation Request", cr.full_name, cr.work_email, cr.organization, cr.status, cr.created_at.strftime("%Y-%m-%d")])
    return response
