from django.urls import path

from . import student_views as views

app_name = "student_labs"

urlpatterns = [
    path("", views.lab_list, name="list"),
    path("<uuid:lab_id>/", views.lab_detail, name="detail"),
]
