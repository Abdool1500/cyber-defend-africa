from django.urls import path

from . import dashboard_views as views

app_name = "instructor_dashboard"

urlpatterns = [
    path("", views.instructor_overview, name="overview"),
    path("courses/", views.instructor_courses, name="courses"),
    path("students/", views.instructor_students, name="students"),
]
