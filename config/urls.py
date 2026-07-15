"""
URL configuration for the Cyber Defend Africa LTD platform.

Grows one `include()` at a time as each app/phase is built — see
tasks/todo.md for what's implemented so far.
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from apps.academy.views import CareerPathAssessmentView
from apps.core.sitemaps import CourseSitemap, ResourceSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "courses": CourseSitemap,
    "resources": ResourceSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots_txt"),
    path("", include("apps.core.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("", include("apps.company.urls")),
    path("academy/", include("apps.academy.urls")),
    path("career-path-assessment/", CareerPathAssessmentView.as_view(), name="career_path_assessment"),
    path("courses/", include("apps.courses.urls")),
    path("resources/", include("apps.resources.urls")),
    path("", include("apps.leads.urls")),
    path("certificates/", include("apps.certificates.urls")),

    # Student dashboard
    path("student/", include("apps.core.dashboard_student_urls")),
    path("student/learning/", include("apps.enrollments.student_urls")),
    path("student/", include("apps.quizzes.student_urls")),
    path("student/assignments/", include("apps.assignments.student_urls")),
    path("student/feedback/", include("apps.feedback.student_urls")),
    path("student/certificates/", include("apps.certificates.student_urls")),
    path("student/notifications/", include("apps.notifications.urls")),
    path("student/labs/", include("apps.labs.student_urls")),
    path("student/employment/", include("apps.employment.student_urls")),

    # Instructor dashboard
    path("instructor/", include("apps.core.dashboard_instructor_urls")),
    path("instructor/question-bank/", include("apps.question_bank.urls")),
    path("instructor/quizzes/", include("apps.quizzes.instructor_quiz_urls")),
    path("instructor/grading/", include("apps.quizzes.instructor_grading_urls")),
    path("instructor/assignments/", include("apps.assignments.instructor_urls")),
    path("instructor/feedback/", include("apps.feedback.instructor_urls")),
    path("instructor/labs/", include("apps.labs.instructor_urls")),

    # Management dashboard
    path("management/", include("apps.core.dashboard_management_urls")),
    path("management/reports/", include("apps.reports.urls")),
    path("management/cohorts/", include("apps.cohorts.management_urls")),
    path("management/employment/", include("apps.employment.management_urls")),

    # REST API
    path("api/v1/", include("apps.core.api_urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
