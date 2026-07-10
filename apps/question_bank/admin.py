from django.contrib import admin

from .models import Question, QuestionOption


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question_text_short", "course", "question_type", "difficulty", "status", "is_locked", "updated_at"]
    list_filter = ["status", "question_type", "difficulty", "course"]
    search_fields = ["question_text", "topic"]
    readonly_fields = ["id", "is_locked", "created_at", "updated_at"]
    inlines = [QuestionOptionInline]

    def question_text_short(self, obj):
        return obj.question_text[:60]
    question_text_short.short_description = "Question"
