from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("healthz/", views.health_check, name="health_check"),
    path("post-login/", views.post_login_redirect, name="post_login_redirect"),
]
