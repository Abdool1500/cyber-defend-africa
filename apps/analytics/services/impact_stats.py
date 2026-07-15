"""Impact Dashboard aggregation (16.K) — combines the genuinely-computed
platform metrics from platform_stats.py with the admin-entered
ImpactSnapshot figures that can't be derived from any tracked LMS
event. The two are kept in clearly separate dict keys
("computed"/"self_reported") rather than merged into one flat dict, so
the template can never accidentally present a self-reported number as
a measured one.
"""
from apps.enrollments.models import Enrollment
from apps.labs.models import LabProgress

from ..models import ImpactSnapshot
from .platform_stats import get_platform_analytics


def _latest_impact_snapshot():
    snapshot = ImpactSnapshot.objects.first()  # Meta.ordering = ["-created_at"]
    if snapshot is None:
        return {
            "smes_protected": None,
            "healthcare_workers_trained": None,
            "businesses_started": None,
            "as_of": None,
        }
    return {
        "smes_protected": snapshot.smes_protected,
        "healthcare_workers_trained": snapshot.healthcare_workers_trained,
        "businesses_started": snapshot.businesses_started,
        "as_of": snapshot.created_at,
    }


def get_impact_dashboard_data():
    platform = get_platform_analytics()
    people_trained = Enrollment.objects.values("student_id").distinct().count()
    labs_completed = LabProgress.objects.filter(status=LabProgress.Status.COMPLETED).count()

    return {
        "computed": {
            "people_trained": people_trained,
            "certificates_issued": platform["certificates_issued"],
            "total_learning_hours": platform["total_learning_hours"],
            "labs_completed": labs_completed,
            "completion_rate": platform["completion_rate"],
            "average_score": platform["average_score"],
            "avg_skill_improvement": platform["avg_skill_improvement"],
            "employment_rate": platform["employment"]["employment_rate"],
            "nps_score": platform["nps"]["nps_score"],
        },
        "self_reported": _latest_impact_snapshot(),
    }
