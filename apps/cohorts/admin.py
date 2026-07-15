from django.contrib import admin

from .models import Cohort, CohortMembership


class CohortMembershipInline(admin.TabularInline):
    model = CohortMembership
    extra = 1
    autocomplete_fields = ["student"]


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ["name", "start_date", "end_date", "created_by", "created_at"]
    search_fields = ["name"]
    autocomplete_fields = ["created_by"]
    inlines = [CohortMembershipInline]


@admin.register(CohortMembership)
class CohortMembershipAdmin(admin.ModelAdmin):
    list_display = ["student", "cohort", "joined_at"]
    list_filter = ["cohort"]
    search_fields = ["student__email", "cohort__name"]
    autocomplete_fields = ["cohort", "student"]
