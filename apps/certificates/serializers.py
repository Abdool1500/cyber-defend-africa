from rest_framework import serializers

from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Certificate
        fields = [
            "id", "course", "course_title", "certificate_number", "verification_code",
            "certificate_hash", "issued_at", "status",
        ]
        read_only_fields = fields
