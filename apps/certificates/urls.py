from django.urls import path

from . import views

app_name = "certificates"

urlpatterns = [
    path("verify/<str:code>/", views.verify_certificate, name="verify"),
    path("verify/<str:code>/qr.png", views.certificate_qr_code, name="qr_code"),
]
