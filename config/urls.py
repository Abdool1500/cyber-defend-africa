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
    path("certificates/", include("apps.certificates.urls")),

    # Student dashboard
    path("student/", include("apps.core.dashboard_student_urls")),
    path("student/", include("apps.quizzes.student_urls")),
    path("student/assignments/", include("apps.assignments.student_urls")),
    path("student/feedback/", include("apps.feedback.student_urls")),
    path("student/certificates/", include("apps.certificates.student_urls")),

    # Instructor dashboard
    path("instructor/", include("apps.core.dashboard_instructor_urls")),
    path("instructor/question-bank/", include("apps.question_bank.urls")),
    path("instructor/quizzes/", include("apps.quizzes.instructor_quiz_urls")),
    path("instructor/grading/", include("apps.quizzes.instructor_grading_urls")),
    path("instructor/assignments/", include("apps.assignments.instructor_urls")),
    path("instructor/feedback/", include("apps.feedback.instructor_urls")),

    # Management dashboard
    path("management/", include("apps.core.dashboard_management_urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
