from django.urls import path

from . import dashboard_views as views

app_name = "student_dashboard"

urlpatterns = [
    path("", views.student_overview, name="overview"),
    path("courses/", views.student_courses, name="courses"),
]
