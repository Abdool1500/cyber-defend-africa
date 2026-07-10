import csv

from django.http import HttpResponse
from django.shortcuts import render

from apps.accounts.permissions import admin_required
from apps.enrollments.models import Enrollment
from apps.leads.models import ConsultationRequest, ContactSubmission, DemoRequest, PilotRequest


@admin_required
def reports_index(request):
    return render(request, "management/reports/index.html")


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
