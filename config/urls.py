"""
URL configuration for the Cyber Defend Africa LTD platform.

Grows one `include()` at a time as each app/phase is built — see
tasks/todo.md for what's implemented so far.
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("", include("apps.company.urls")),
    path("academy/", include("apps.academy.urls")),
    path("courses/", include("apps.courses.urls")),
    path("resources/", include("apps.resources.urls")),
    path("", include("apps.leads.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
