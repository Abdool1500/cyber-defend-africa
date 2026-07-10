from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("waitlist/", views.WaitlistView.as_view(), name="waitlist"),
    path("gpt-sentinel/demo-request/", views.DemoRequestView.as_view(), name="demo_request"),
    path("gpt-sentinel/pilot-request/", views.PilotRequestView.as_view(), name="pilot_request"),
    path("services/consultation-request/", views.ConsultationRequestView.as_view(), name="consultation_request"),
]
