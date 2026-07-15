"""Plain (non-ModelSerializer) serializers that shape the dict outputs
of apps.analytics.services for the REST API (16.M) — these read-only
dashboards are computed on every call, not backed by a single model, so
there's no queryset for a ModelSerializer to bind to.
"""
from rest_framework import serializers


class NPSSerializer(serializers.Serializer):
    total_responses = serializers.IntegerField()
    promoters = serializers.IntegerField()
    passives = serializers.IntegerField()
    detractors = serializers.IntegerField()
    promoter_pct = serializers.FloatField(allow_null=True)
    passive_pct = serializers.FloatField(allow_null=True)
    detractor_pct = serializers.FloatField(allow_null=True)
    nps_score = serializers.IntegerField(allow_null=True)


class EmploymentSummarySerializer(serializers.Serializer):
    total_reporting = serializers.IntegerField()
    employed_count = serializers.IntegerField()
    employment_rate = serializers.FloatField()
    status_breakdown = serializers.ListField(child=serializers.DictField())


class PlatformAnalyticsSerializer(serializers.Serializer):
    dau = serializers.IntegerField()
    mau = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    dropout_rate = serializers.FloatField()
    retention_rate = serializers.FloatField()
    average_score = serializers.FloatField(allow_null=True)
    avg_pre_test = serializers.FloatField(allow_null=True)
    avg_post_test = serializers.FloatField(allow_null=True)
    avg_skill_improvement = serializers.FloatField(allow_null=True)
    certificates_issued = serializers.IntegerField()
    certificates_this_month = serializers.IntegerField()
    total_learning_hours = serializers.FloatField()
    top_courses = serializers.ListField(child=serializers.DictField())
    top_instructors = serializers.ListField(child=serializers.DictField())
    employment = EmploymentSummarySerializer()
    nps = NPSSerializer()


class ImpactComputedSerializer(serializers.Serializer):
    people_trained = serializers.IntegerField()
    certificates_issued = serializers.IntegerField()
    total_learning_hours = serializers.FloatField()
    labs_completed = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_score = serializers.FloatField(allow_null=True)
    avg_skill_improvement = serializers.FloatField(allow_null=True)
    employment_rate = serializers.FloatField()
    nps_score = serializers.IntegerField(allow_null=True)


class ImpactSelfReportedSerializer(serializers.Serializer):
    smes_protected = serializers.IntegerField(allow_null=True)
    healthcare_workers_trained = serializers.IntegerField(allow_null=True)
    businesses_started = serializers.IntegerField(allow_null=True)
    as_of = serializers.DateTimeField(allow_null=True)


class ImpactDashboardSerializer(serializers.Serializer):
    computed = ImpactComputedSerializer()
    self_reported = ImpactSelfReportedSerializer()
