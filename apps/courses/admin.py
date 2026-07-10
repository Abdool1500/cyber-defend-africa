from django.contrib import admin

from .models import Course, CourseModule, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "level", "status", "category", "updated_at"]
    list_filter = ["status", "level", "category"]
    search_fields = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CourseModuleInline]


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "display_order", "status"]
    list_filter = ["status", "course"]
    search_fields = ["title"]
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "module", "lesson_type", "display_order", "status", "is_preview"]
    list_filter = ["status", "lesson_type", "is_preview"]
    search_fields = ["title"]
