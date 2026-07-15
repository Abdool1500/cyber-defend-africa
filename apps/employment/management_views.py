from django.shortcuts import render

from apps.accounts.permissions import admin_required
from apps.analytics.services.employment_stats import get_employment_summary


@admin_required
def employment_summary(request):
    summary = get_employment_summary()
    return render(request, "management/employment/summary.html", {"summary": summary})
