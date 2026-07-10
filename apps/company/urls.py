from django.urls import path

from . import views

app_name = "company"

urlpatterns = [
    path("about/", views.AboutView.as_view(), name="about"),
    path("solutions/", views.SolutionsView.as_view(), name="solutions"),
    path("gpt-sentinel/", views.GPTSentinelView.as_view(), name="gpt_sentinel"),
    path("services/", views.ServicesView.as_view(), name="services"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
    path("terms/", views.TermsView.as_view(), name="terms"),
    path("cookies/", views.CookiesView.as_view(), name="cookies"),
    path("responsible-disclosure/", views.ResponsibleDisclosureView.as_view(), name="responsible_disclosure"),
    path("acceptable-use/", views.AcceptableUseView.as_view(), name="acceptable_use"),
]
