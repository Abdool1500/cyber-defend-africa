from .base import *  # noqa: F401,F403

DEBUG = True

if "testserver" not in ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS.append("testserver")  # noqa: F405

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
