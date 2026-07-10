from django.urls import path

from . import student_views as views

app_name = "student_assignments"

urlpatterns = [
    path("", views.assignment_list, name="list"),
    path("<uuid:assignment_id>/", views.assignment_detail, name="detail"),
]
