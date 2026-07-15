from django.urls import path

from . import student_views as views

app_name = "student_employment"

urlpatterns = [
    path("", views.employment_list, name="list"),
    path("new/", views.employment_create, name="create"),
]
