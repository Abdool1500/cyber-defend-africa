from django.urls import path

from . import student_views as views

app_name = "student_learning"

urlpatterns = [
    path("<uuid:course_id>/", views.course_overview, name="course_overview"),
    path("<uuid:course_id>/<uuid:lesson_id>/", views.lesson_detail, name="lesson_detail"),
    path("<uuid:course_id>/<uuid:lesson_id>/heartbeat/", views.lesson_heartbeat, name="lesson_heartbeat"),
]
