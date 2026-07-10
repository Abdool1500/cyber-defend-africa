from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import (
    ConsultationRequestForm,
    ContactForm,
    DemoRequestForm,
    NewsletterSubscribeForm,
    PilotRequestForm,
)


class ContactView(FormView):
    template_name = "public/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("leads:contact")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Thanks — we've received your message and will be in touch.")
        return super().form_valid(form)


class DemoRequestView(FormView):
    template_name = "public/demo_request.html"
    form_class = DemoRequestForm
    success_url = reverse_lazy("leads:demo_request")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Thanks — your demo request has been received.")
        return super().form_valid(form)


class PilotRequestView(FormView):
    template_name = "public/pilot_request.html"
    form_class = PilotRequestForm
    success_url = reverse_lazy("leads:pilot_request")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Thanks — your pilot interest has been registered.")
        return super().form_valid(form)


class ConsultationRequestView(FormView):
    template_name = "public/consultation_request.html"
    form_class = ConsultationRequestForm
    success_url = reverse_lazy("leads:consultation_request")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Thanks — we'll follow up about a consultation soon.")
        return super().form_valid(form)


class WaitlistView(FormView):
    template_name = "public/waitlist.html"
    form_class = NewsletterSubscribeForm
    success_url = reverse_lazy("leads:waitlist")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        from .models import NewsletterSubscriber

        NewsletterSubscriber.objects.update_or_create(
            email=email, defaults={"status": "subscribed", "source": "waitlist_page"}
        )
        messages.success(self.request, "Thanks — we'll keep you updated. Don't forget to open the waitlist form too.")
        return super().form_valid(form)
