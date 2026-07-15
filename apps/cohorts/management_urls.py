from django.urls import path

from . import management_views as views

app_name = "management_cohorts"

urlpatterns = [
    path("", views.cohort_list, name="list"),
    path("<uuid:cohort_id>/", views.cohort_detail, name="detail"),
]
