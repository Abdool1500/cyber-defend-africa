from django.urls import path

from . import instructor_views as views

app_name = "instructor_feedback"

urlpatterns = [
    path("", views.feedback_list, name="list"),
    path("analytics/", views.feedback_analytics, name="analytics"),
    path("export/csv/", views.feedback_export_csv, name="export_csv"),
    path("export/pdf/", views.feedback_export_pdf, name="export_pdf"),
]
