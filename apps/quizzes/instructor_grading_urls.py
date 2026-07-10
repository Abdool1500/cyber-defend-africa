from django.urls import path

from . import instructor_views as views

app_name = "instructor_grading"

urlpatterns = [
    path("", views.grading_list, name="list"),
    path("<uuid:attempt_id>/", views.grading_detail, name="detail"),
]
