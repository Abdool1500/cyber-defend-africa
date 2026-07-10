from django.conf import settings
from django.views.generic import TemplateView

from .data import SERVICES, SOLUTIONS

GPT_SENTINEL_STAGE_LABELS = {
    "development": "In Development",
    "prototype": "Prototype",
    "private_preview": "Private Preview",
    "pilot": "Pilot",
    "early_access": "Early Access",
    "available": "Available",
}


class AboutView(TemplateView):
    template_name = "public/about.html"


class SolutionsView(TemplateView):
    template_name = "public/solutions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["solutions"] = SOLUTIONS
        return context


class GPTSentinelView(TemplateView):
    template_name = "public/gpt_sentinel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["features"] = [
            "AI-Assisted Alert Triage",
            "Incident Summarization",
            "Investigation Copilot",
            "Threat Context Enrichment",
            "Risk-Based Prioritization",
            "MITRE ATT&CK Mapping",
            "Recommended Next Actions",
            "Natural Language Security Interface",
            "Analyst Workflow Support",
            "Human-in-the-Loop Review",
        ]
        context["how_it_works"] = [
            "Alert Received",
            "Context Collected",
            "AI-Assisted Analysis",
            "Risk Prioritization",
            "Investigation Summary",
            "Analyst Review",
            "Response Decision",
        ]
        context["intended_users"] = [
            "SOC teams",
            "Cybersecurity analysts",
            "SMEs",
            "Healthcare organizations",
            "Educational institutions",
            "Critical infrastructure teams",
            "MSSPs",
            "Organizations with limited security staffing",
        ]
        context["stage_label"] = GPT_SENTINEL_STAGE_LABELS.get(
            settings.GPT_SENTINEL_STAGE, "In Development"
        )
        return context


class ServicesView(TemplateView):
    template_name = "public/services.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = SERVICES
        return context


class PrivacyView(TemplateView):
    template_name = "public/legal/privacy.html"


class TermsView(TemplateView):
    template_name = "public/legal/terms.html"


class CookiesView(TemplateView):
    template_name = "public/legal/cookies.html"


class ResponsibleDisclosureView(TemplateView):
    template_name = "public/legal/responsible_disclosure.html"


class AcceptableUseView(TemplateView):
    template_name = "public/legal/acceptable_use.html"
