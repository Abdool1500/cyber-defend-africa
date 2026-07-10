from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Course
from .serializers import CourseDetailSerializer, CourseSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Public read-only course catalog — published courses only. No
    correct-answer or private data is ever exposed here."""

    queryset = Course.objects.filter(status=Course.Status.PUBLISHED)
    permission_classes = [AllowAny]
    lookup_field = "slug"
    filterset_fields = ["category", "level"]
    search_fields = ["title", "short_description"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer
