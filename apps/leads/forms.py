from django import forms

from apps.core.forms import BootstrapFormMixin

from .models import ConsultationRequest, ContactSubmission, DemoRequest, NewsletterSubscriber, PilotRequest


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ["full_name", "email", "phone", "organization", "country", "inquiry_type", "message", "consent"]

    def clean_consent(self):
        consent = self.cleaned_data["consent"]
        if not consent:
            raise forms.ValidationError("Please confirm you consent to being contacted.")
        return consent


class DemoRequestForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = DemoRequest
        fields = [
            "full_name", "work_email", "organization", "role", "country",
            "organization_size", "security_team_size", "current_challenge",
            "message", "consent",
        ]

    def clean_consent(self):
        consent = self.cleaned_data["consent"]
        if not consent:
            raise forms.ValidationError("Please confirm you consent to being contacted.")
        return consent


class PilotRequestForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PilotRequest
        fields = [
            "full_name", "work_email", "organization", "role", "country",
            "organization_type", "use_case", "current_challenge", "message",
        ]


class ConsultationRequestForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ["full_name", "work_email", "organization", "country", "service_type", "message"]


class NewsletterSubscribeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]
