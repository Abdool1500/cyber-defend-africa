from django.urls import path

from . import management_views as views

app_name = "management_employment"

urlpatterns = [
    path("", views.employment_summary, name="summary"),
]
