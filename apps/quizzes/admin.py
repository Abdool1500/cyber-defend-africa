from django.contrib import admin

from .models import AttemptQuestion, Quiz, QuizAnswer, QuizAttempt, QuizQuestion, QuizRandomRule


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0


class QuizRandomRuleInline(admin.TabularInline):
    model = QuizRandomRule
    extra = 0


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "status", "attempt_limit", "passing_score", "updated_at"]
    list_filter = ["status", "course"]
    search_fields = ["title"]
    inlines = [QuizQuestionInline, QuizRandomRuleInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ["student", "quiz", "attempt_number", "status", "percentage", "started_at"]
    list_filter = ["status"]
    search_fields = ["student__email", "quiz__title"]
    readonly_fields = ["id", "started_at", "submitted_at", "graded_at"]


@admin.register(AttemptQuestion)
class AttemptQuestionAdmin(admin.ModelAdmin):
    list_display = ["attempt", "question", "display_order", "points"]
    search_fields = ["attempt__student__email"]


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ["attempt", "student", "is_correct", "awarded_points"]
    list_filter = ["is_correct"]
    search_fields = ["student__email"]
