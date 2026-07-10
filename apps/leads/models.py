import uuid

from django.db import models


class ContactSubmission(models.Model):
    class InquiryType(models.TextChoices):
        GENERAL = "general", "General Inquiry"
        ACADEMY = "academy", "Academy Inquiry"
        ENTERPRISE = "enterprise", "Enterprise Security Services"
        GPT_SENTINEL_DEMO = "gpt_sentinel_demo", "GPT Sentinel Demo"
        PARTNERSHIP = "partnership", "Partnership Inquiry"
        MEDIA = "media", "Media Inquiry"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=32, null=True, blank=True)
    organization = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    inquiry_type = models.CharField(max_length=30, choices=InquiryType.choices, default=InquiryType.GENERAL)
    message = models.TextField()
    consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.get_inquiry_type_display()}"


class DemoRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=150)
    work_email = models.EmailField()
    organization = models.CharField(max_length=200)
    role = models.CharField(max_length=150)
    country = models.CharField(max_length=100)
    organization_size = models.CharField(max_length=100)
    security_team_size = models.CharField(max_length=100, null=True, blank=True)
    current_challenge = models.TextField()
    message = models.TextField(blank=True)
    consent = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.organization})"


class PilotRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=150)
    work_email = models.EmailField()
    organization = models.CharField(max_length=200)
    role = models.CharField(max_length=150)
    country = models.CharField(max_length=100)
    organization_type = models.CharField(max_length=150)
    use_case = models.TextField()
    current_challenge = models.TextField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.organization})"


class ConsultationRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=150)
    work_email = models.EmailField()
    organization = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    service_type = models.CharField(max_length=150)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.organization})"


class NewsletterSubscriber(models.Model):
    class Status(models.TextChoices):
        SUBSCRIBED = "subscribed", "Subscribed"
        UNSUBSCRIBED = "unsubscribed", "Unsubscribed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBSCRIBED)
    source = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
