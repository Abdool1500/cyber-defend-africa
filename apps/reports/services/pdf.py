"""Branded PDF report generation using ReportLab. Kept as small, focused
builder functions per report type rather than one generic PDF engine —
each report has different fields and privacy rules (e.g. feedback
anonymity), so a shared abstraction would just hide those differences.
"""
import io

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

    data = [["Course", "Respondent", "Overall", "Content", "Lab", "Platform", "Submitted"]]
    for f in feedback_queryset:
        data.append([
            f.course.title,
            f.display_name(),
            str(f.overall_rating),
            str(f.content_quality),
            str(f.practical_lab_quality),
            str(f.platform_experience),
            f.created_at.strftime("%Y-%m-%d"),
        ])

    if len(data) == 1:
        story.append(Paragraph("No feedback responses match the selected filters.", styles["Normal"]))
    else:
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b2545")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        story.append(table)

    doc.build(story)
    return buffer.getvalue()
