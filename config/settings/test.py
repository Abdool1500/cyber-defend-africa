from .base import *  # noqa: F401,F403

DEBUG = False

# Let real exceptions raised inside views propagate to the test runner
# instead of being rendered into an HTML error response — on this
# Django/Python combination, rendering the technical 500 page inside the
# test client crashes on an unrelated RequestContext.__copy__ issue and
# masks the actual traceback we need to see.
DEBUG_PROPAGATE_EXCEPTIONS = True

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
