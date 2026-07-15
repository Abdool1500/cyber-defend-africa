"""Branded PDF report generation using ReportLab. Kept as small, focused
builder functions per report type rather than one generic PDF engine —
each report has different fields and privacy rules (e.g. feedback
anonymity), so a shared abstraction would just hide those differences.
"""
import io
from xml.sax.saxutils import escape

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet


def _base_doc(buffer, title):
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Cyber Defend Africa LTD", styles["Title"]),
        Paragraph(title, styles["Heading2"]),
        Paragraph(f"Generated {timezone.now().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]),
        Spacer(1, 0.5 * cm),
    ]
    return doc, styles, story


def _styled_table(data):
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b2545")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    return table


def build_feedback_report_pdf(feedback_queryset, generated_for=None) -> bytes:
    """Builds a feedback summary PDF. Anonymous respondents are always
    rendered as 'Anonymous Student' — display_name() on the model is the
    only place identity is resolved, so this function never touches
    feedback.student directly."""
    buffer = io.BytesIO()
    doc, styles, story = _base_doc(buffer, "Student Feedback Report")

    if generated_for:
        story.append(Paragraph(f"Prepared for: {generated_for.full_name}", styles["Normal"]))
        story.append(Spacer(1, 0.3 * cm))

    data = [["Course", "Respondent", "Overall", "Content", "Lab", "Platform", "NPS", "Submitted"]]
    for f in feedback_queryset:
        data.append([
            f.course.title,
            f.display_name(),
            str(f.overall_rating),
            str(f.content_quality),
            str(f.practical_lab_quality),
            str(f.platform_experience),
            str(f.nps_score),
            f.created_at.strftime("%Y-%m-%d"),
        ])

    if len(data) == 1:
        story.append(Paragraph("No feedback responses match the selected filters.", styles["Normal"]))
    else:
        story.append(_styled_table(data))

    doc.build(story)
    return buffer.getvalue()


def build_impact_report_pdf(impact) -> bytes:
    buffer = io.BytesIO()
    doc, styles, story = _base_doc(buffer, "Impact Report")

    story.append(Paragraph("Measured (Computed From Platform Data)", styles["Heading3"]))
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
    computed_data = [["Metric", "Value"]] + [
        [label, str(impact["computed"][key])] for key, label in computed_labels.items()
    ]
    story.append(_styled_table(computed_data))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Self-Reported (Not Derived From LMS Data)", styles["Heading3"]))
    self_reported_labels = {
        "smes_protected": "SMEs Protected",
        "healthcare_workers_trained": "Healthcare Workers Trained",
        "businesses_started": "Businesses Started",
    }
    self_reported_data = [["Metric", "Value"]] + [
        [label, str(impact["self_reported"][key])] for key, label in self_reported_labels.items()
    ]
    story.append(_styled_table(self_reported_data))
    as_of = impact["self_reported"]["as_of"]
    if as_of:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"Self-reported figures as of {as_of.strftime('%Y-%m-%d')}.", styles["Normal"]))

    doc.build(story)
    return buffer.getvalue()


def build_course_report_pdf(rows) -> bytes:
    buffer = io.BytesIO()
    doc, styles, story = _base_doc(buffer, "Course Report")

    data = [["Course", "Enrollments", "Completed", "Completion %", "Avg Score", "Avg Rating", "Certificates"]]
    for row in rows:
        data.append([
            row["course_title"], str(row["total_enrollments"]), str(row["completed_enrollments"]),
            str(row["completion_rate"]), str(row["average_score"]), str(row["average_rating"]),
            str(row["certificates_issued"]),
        ])

    if len(data) == 1:
        story.append(Paragraph("No courses to report on.", styles["Normal"]))
    else:
        story.append(_styled_table(data))

    doc.build(story)
    return buffer.getvalue()


def build_student_report_pdf(rows) -> bytes:
    buffer = io.BytesIO()
    doc, styles, story = _base_doc(buffer, "Student Report")

    data = [["Student", "Email", "Enrollments", "Completed", "Avg Score", "Certificates", "Learning Hours"]]
    for row in rows:
        data.append([
            row["student_name"], row["student_email"], str(row["total_enrollments"]),
            str(row["completed_enrollments"]), str(row["average_score"]), str(row["certificates_earned"]),
            str(row["learning_hours"]),
        ])

    if len(data) == 1:
        story.append(Paragraph("No students to report on.", styles["Normal"]))
    else:
        story.append(_styled_table(data))

    doc.build(story)
    return buffer.getvalue()


def build_employment_report_pdf(employment) -> bytes:
    """Aggregate-only, matching the management-facing Employment Outcomes
    page — never salary or evidence, per the Phase 16 planning decision
    (see apps.analytics.services.employment_stats)."""
    buffer = io.BytesIO()
    doc, styles, story = _base_doc(buffer, "Employment Report")

    data = [["Status", "Count"]]
    for row in employment["status_breakdown"]:
        data.append([row["label"], str(row["count"])])
    story.append(_styled_table(data))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(f"Total Reporting: {employment['total_reporting']}", styles["Normal"]))
    story.append(Paragraph(f"Employment Rate: {employment['employment_rate']}%", styles["Normal"]))

    doc.build(story)
    return buffer.getvalue()


def build_fid_impact_report_pdf(data) -> bytes:
    """A single funder-facing rollup PDF grouped into the sections a
    grant/impact report typically wants — every figure here is already
    computed by an existing service (see
    apps.analytics.services.fid_report), this function only lays it
    out."""
    buffer = io.BytesIO()
    doc, styles, story = _base_doc(buffer, "Impact Evidence Report")

    if data["prepared_for"]:
        # escape() is required, not optional — ReportLab's Paragraph
        # parses a small XML-like markup language, and prepared_for
        # comes from a query param (see apps.reports.views.export_fid_pdf),
        # so unescaped input could break PDF generation with malformed tags.
        story.append(Paragraph(f"Prepared for: {escape(data['prepared_for'])}", styles["Normal"]))
        story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Reach", styles["Heading3"]))
    reach = data["reach"]
    story.append(_styled_table([
        ["Metric", "Value"],
        ["People Trained", str(reach["people_trained"])],
        ["Certificates Issued", str(reach["certificates_issued"])],
        ["Total Learning Hours", str(reach["total_learning_hours"])],
        ["Labs Completed", str(reach["labs_completed"])],
    ]))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Learning Outcomes", styles["Heading3"]))
    outcomes = data["learning_outcomes"]
    story.append(_styled_table([
        ["Metric", "Value"],
        ["Completion Rate (%)", str(outcomes["completion_rate"])],
        ["Average Quiz Score (%)", str(outcomes["average_score"])],
        ["Average Skill Improvement (%)", str(outcomes["avg_skill_improvement"])],
        ["Net Promoter Score", str(outcomes["nps_score"])],
    ]))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Employment Outcomes", styles["Heading3"]))
    employment = data["employment_outcomes"]
    employment_data = [["Status", "Count"]] + [
        [row["label"], str(row["count"])] for row in employment["status_breakdown"]
    ]
    story.append(_styled_table(employment_data))
    story.append(Paragraph(
        f"Total Reporting: {employment['total_reporting']} — "
        f"Employment Rate: {employment['employment_rate']}%",
        styles["Normal"],
    ))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Field Impact (Self-Reported)", styles["Heading3"]))
    field = data["field_impact"]
    story.append(_styled_table([
        ["Metric", "Value"],
        ["SMEs Protected", str(field["smes_protected"])],
        ["Healthcare Workers Trained", str(field["healthcare_workers_trained"])],
        ["Businesses Started", str(field["businesses_started"])],
    ]))
    if field["as_of"]:
        story.append(Paragraph(f"As of {field['as_of'].strftime('%Y-%m-%d')}.", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    if data["cohorts"]:
        story.append(Paragraph("Cohort Breakdown", styles["Heading3"]))
        cohort_data = [["Cohort", "Members", "Completion %", "Avg Score", "Certificates"]]
        for cohort in data["cohorts"]:
            cohort_data.append([
                cohort["name"], str(cohort["member_count"]), str(cohort["completion_rate"]),
                str(cohort["average_score"]), str(cohort["certificates_earned"]),
            ])
        story.append(_styled_table(cohort_data))
        story.append(Spacer(1, 0.5 * cm))

    if data["top_courses"]:
        story.append(Paragraph("Top Courses by Enrollment", styles["Heading3"]))
        course_data = [["Course", "Enrollments"]] + [
            [row["course__title"], str(row["enrollment_count"])] for row in data["top_courses"]
        ]
        story.append(_styled_table(course_data))

    doc.build(story)
    return buffer.getvalue()
