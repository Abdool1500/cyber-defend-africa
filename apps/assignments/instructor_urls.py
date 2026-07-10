from django.urls import path

from . import instructor_views as views

app_name = "instructor_assignments"

urlpatterns = [
    path("", views.assignment_list, name="list"),
    path("new/", views.assignment_create, name="create"),
    path("<uuid:assignment_id>/edit/", views.assignment_edit, name="edit"),
    path("<uuid:assignment_id>/submissions/", views.submission_list, name="submissions"),
    path("<uuid:assignment_id>/submissions/<uuid:submission_id>/grade/", views.submission_grade, name="grade"),
]
