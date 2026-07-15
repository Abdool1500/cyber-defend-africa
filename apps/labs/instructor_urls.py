from django.urls import path

from . import instructor_views as views

app_name = "instructor_labs"

urlpatterns = [
    path("", views.lab_list, name="list"),
    path("new/", views.lab_create, name="create"),
    path("<uuid:lab_id>/edit/", views.lab_edit, name="edit"),
    path("<uuid:lab_id>/progress/", views.lab_progress_list, name="progress_list"),
    path("<uuid:lab_id>/progress/<uuid:progress_id>/grade/", views.lab_grade, name="grade"),
]
