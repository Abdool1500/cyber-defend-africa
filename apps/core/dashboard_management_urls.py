from django.urls import path

from . import dashboard_views as views

app_name = "management"

urlpatterns = [
    path("", views.management_overview, name="overview"),
]
