from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_index, name="index"),
    path("enrollments/export/csv/", views.export_enrollments_csv, name="export_enrollments_csv"),
    path("leads/export/csv/", views.export_leads_csv, name="export_leads_csv"),
]
