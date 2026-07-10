from django.urls import path

from . import student_views as views

app_name = "student_feedback"

urlpatterns = [
    path("", views.feedback_list, name="list"),
    path("<uuid:course_id>/new/", views.feedback_create, name="create"),
]
