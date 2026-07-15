from django.shortcuts import get_object_or_404, render

from apps.accounts.permissions import admin_required
from apps.analytics.services.cohort_stats import get_cohort_stats

from .models import Cohort


@admin_required
def cohort_list(request):
    cohorts = Cohort.objects.all()
    rows = [(cohort, get_cohort_stats(cohort)) for cohort in cohorts]
    return render(request, "management/cohorts/list.html", {"rows": rows})


@admin_required
def cohort_detail(request, cohort_id):
    cohort = get_object_or_404(Cohort, id=cohort_id)
    stats = get_cohort_stats(cohort)
    members = cohort.memberships.select_related("student").order_by("student__full_name")
    return render(request, "management/cohorts/detail.html", {
        "cohort": cohort, "stats": stats, "members": members,
    })
