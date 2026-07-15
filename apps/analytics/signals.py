"""Login/logout session tracking for LearningSession — connected via
AnalyticsConfig.ready(). See models.py for why this is separate from
LearningTimeEntry (session time vs. actual content-engagement time)."""
import datetime

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone

from .models import LearningSession

MAX_SESSION_HOURS = 4


@receiver(user_logged_in)
def start_learning_session(sender, request, user, **kwargs):
    # Close any session left open by an abandoned browser tab (no
    # explicit logout) before starting a fresh one — capped at a
    # reasonable max so an abandoned session doesn't look like the user
    # was logged in for days.
    stale_sessions = LearningSession.objects.filter(user=user, ended_at__isnull=True)
    for session in stale_sessions:
        capped_end = min(timezone.now(), session.started_at + datetime.timedelta(hours=MAX_SESSION_HOURS))
        session.ended_at = capped_end
        session.save(update_fields=["ended_at"])

    LearningSession.objects.create(user=user)


@receiver(user_logged_out)
def end_learning_session(sender, request, user, **kwargs):
    if user is None:
        return
    session = LearningSession.objects.filter(user=user, ended_at__isnull=True).order_by("-started_at").first()
    if session:
        session.ended_at = timezone.now()
        session.save(update_fields=["ended_at"])
