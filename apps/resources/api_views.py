from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import ResourcePost
from .serializers import ResourcePostSerializer


class ResourcePostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResourcePost.objects.filter(status=ResourcePost.Status.PUBLISHED).select_related("category")
    serializer_class = ResourcePostSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
    search_fields = ["title", "excerpt"]
