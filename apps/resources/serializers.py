from rest_framework import serializers

from .models import ResourcePost


class ResourcePostSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)

    class Meta:
        model = ResourcePost
        fields = ["id", "title", "slug", "excerpt", "category_name", "featured", "published_at"]
        read_only_fields = fields
