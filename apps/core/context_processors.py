from django.conf import settings


def site_config(request):
    """Exposes non-secret site configuration to every template.

    Never add SUPABASE_SERVICE_ROLE_KEY or any other secret here — this
    context is rendered into HTML sent to the browser.
    """
    waitlist_url = settings.WAITLIST_FORM_URL
    if not waitlist_url.startswith("https://"):
        waitlist_url = ""
    return {
        "WAITLIST_FORM_URL": waitlist_url,
        "GPT_SENTINEL_STAGE": settings.GPT_SENTINEL_STAGE,
        "SITE_URL": settings.SITE_URL,
        "SUPABASE_URL": settings.SUPABASE_URL,
    }
