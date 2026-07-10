from django.contrib import admin

from .models import ResourceCategory, ResourcePost


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ResourcePost)
class ResourcePostAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "author", "status", "featured", "published_at"]
    list_filter = ["status", "featured", "category"]
    search_fields = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ["author"]
