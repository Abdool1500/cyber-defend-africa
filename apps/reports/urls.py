from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_index, name="index"),
    path("analytics/", views.analytics_dashboard, name="analytics_dashboard"),
    path("impact/", views.impact_dashboard, name="impact_dashboard"),
    path("impact/export/csv/", views.export_impact_csv, name="export_impact_csv"),
    path("impact/export/excel/", views.export_impact_excel, name="export_impact_excel"),
    path("impact/export/pdf/", views.export_impact_pdf, name="export_impact_pdf"),
    path("course/export/csv/", views.export_course_csv, name="export_course_csv"),
    path("course/export/excel/", views.export_course_excel, name="export_course_excel"),
    path("course/export/pdf/", views.export_course_pdf, name="export_course_pdf"),
    path("student/export/csv/", views.export_student_csv, name="export_student_csv"),
    path("student/export/excel/", views.export_student_excel, name="export_student_excel"),
    path("student/export/pdf/", views.export_student_pdf, name="export_student_pdf"),
    path("employment/export/csv/", views.export_employment_csv, name="export_employment_csv"),
    path("employment/export/excel/", views.export_employment_excel, name="export_employment_excel"),
    path("employment/export/pdf/", views.export_employment_pdf, name="export_employment_pdf"),
    path("fid/export/pdf/", views.export_fid_pdf, name="export_fid_pdf"),
    path("fid/export/excel/", views.export_fid_excel, name="export_fid_excel"),
    path("enrollments/export/csv/", views.export_enrollments_csv, name="export_enrollments_csv"),
    path("leads/export/csv/", views.export_leads_csv, name="export_leads_csv"),
]
