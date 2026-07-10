from django.contrib import admin

from .models import ConsultationRequest, ContactSubmission, DemoRequest, NewsletterSubscriber, PilotRequest


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "inquiry_type", "created_at"]
    list_filter = ["inquiry_type"]
    search_fields = ["full_name", "email", "organization"]
    readonly_fields = ["created_at"]


@admin.register(DemoRequest)
class DemoRequestAdmin(admin.ModelAdmin):
    list_display = ["full_name", "work_email", "organization", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["full_name", "work_email", "organization"]
    readonly_fields = ["created_at"]


@admin.register(PilotRequest)
class PilotRequestAdmin(admin.ModelAdmin):
    list_display = ["full_name", "work_email", "organization", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["full_name", "work_email", "organization"]
    readonly_fields = ["created_at"]


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ["full_name", "work_email", "organization", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["full_name", "work_email", "organization"]
    readonly_fields = ["created_at"]


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "status", "source", "created_at"]
    list_filter = ["status"]
    search_fields = ["email"]
