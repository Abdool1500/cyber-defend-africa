from .base import *  # noqa: F401,F403

DEBUG = False

# Tests run against local SQLite regardless of DATABASE_URL so the suite
# never depends on live Supabase credentials being available in CI.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

WAITLIST_FORM_URL = "https://docs.google.com/forms/d/e/test/viewform"
