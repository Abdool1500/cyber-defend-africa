from django.contrib import admin

from .models import Announcement, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "type", "read_at", "created_at"]
    list_filter = ["type"]
    search_fields = ["user__email", "title"]
    readonly_fields = ["id", "created_at"]


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ["title", "audience", "course", "created_by", "created_at"]
    list_filter = ["audience"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at"]
