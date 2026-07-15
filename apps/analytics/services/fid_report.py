"""FID Impact Evidence report (16.P) — a funder-facing rollup, not a
new metric source. Every figure here is pulled from services that
already exist (16.J/16.K/16.F/16.H) and grouped into the sections a
funder report typically wants (Reach, Learning Outcomes, Employment
Outcomes, Field Impact, Cohort Breakdown, Top Courses) — nothing is
recomputed, so this can never silently drift from what the
Analytics/Impact dashboards already show.
"""
from django.utils import timezone

from apps.cohorts.models import Cohort

from .cohort_stats import get_cohort_stats
from .employment_stats import get_employment_summary
from .impact_stats import get_impact_dashboard_data
from .platform_stats import get_platform_analytics


def get_fid_impact_report_data(prepared_for=None):
    impact = get_impact_dashboard_data()
    platform = get_platform_analytics()

    cohorts = [
        {"name": cohort.name, **get_cohort_stats(cohort)}
        for cohort in Cohort.objects.all().order_by("name")
    ]

    return {
        "generated_at": timezone.now(),
        "prepared_for": prepared_for,
        "reach": {
            "people_trained": impact["computed"]["people_trained"],
            "certificates_issued": impact["computed"]["certificates_issued"],
            "total_learning_hours": impact["computed"]["total_learning_hours"],
            "labs_completed": impact["computed"]["labs_completed"],
        },
        "learning_outcomes": {
            "completion_rate": impact["computed"]["completion_rate"],
            "average_score": impact["computed"]["average_score"],
            "avg_skill_improvement": impact["computed"]["avg_skill_improvement"],
            "nps_score": impact["computed"]["nps_score"],
        },
        "employment_outcomes": get_employment_summary(),
        "field_impact": impact["self_reported"],
        "cohorts": cohorts,
        "top_courses": platform["top_courses"],
    }
