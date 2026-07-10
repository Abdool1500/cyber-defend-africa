from django.urls import path

from . import views

app_name = "student_certificates"

urlpatterns = [
    path("", views.student_certificate_list, name="list"),
]
