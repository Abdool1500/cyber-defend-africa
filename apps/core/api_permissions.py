from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "student")


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "instructor")


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.role in ("admin", "super_admin")
        )


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "super_admin")


class IsEnrolledStudent(BasePermission):
    """Object-level check: the requesting student must be actively
    enrolled in the course the object belongs to."""

    def has_object_permission(self, request, view, obj):
        from apps.enrollments.models import Enrollment

        course = getattr(obj, "course", obj)
        return Enrollment.objects.filter(
            student=request.user, course=course, status=Enrollment.Status.ACTIVE
        ).exists()


class IsAssignedInstructor(BasePermission):
    """Object-level check: the requesting instructor must be actively
    assigned to the course the object belongs to."""

    def has_object_permission(self, request, view, obj):
        from apps.instructors.models import InstructorAssignment

        course = getattr(obj, "course", obj)
        return InstructorAssignment.objects.filter(
            instructor=request.user, course=course, status=InstructorAssignment.Status.ACTIVE
        ).exists()
