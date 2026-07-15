from rest_framework import serializers

from apps.analytics.services.cohort_stats import get_cohort_stats

from .models import Cohort


class CohortSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Cohort
        fields = ["id", "name", "description", "start_date", "end_date", "stats"]
        read_only_fields = fields

    def get_stats(self, obj) -> dict:
        return get_cohort_stats(obj)
