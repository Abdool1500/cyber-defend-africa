from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, "student/notifications/list.html", {"notifications": notifications})


@login_required
def mark_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    if not notification.read_at:
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at"])
    return redirect("notifications:list")


@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, read_at__isnull=True).update(read_at=timezone.now())
    return redirect("notifications:list")
