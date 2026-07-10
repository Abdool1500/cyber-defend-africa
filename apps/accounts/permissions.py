"""Centralized role-based authorization for Django views.

These are the single source of truth for "who can see this view" — every
dashboard view (student/instructor/management) must use one of these
instead of ad-hoc `if request.user.role == ...` checks scattered around,
and instead of relying on hidden links or JS to hide unauthorized actions.
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def _role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied("You do not have access to this page.")
            if request.user.status != request.user.Status.ACTIVE:
                raise PermissionDenied("Your account is not active.")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def student_required(view_func):
    return _role_required("student")(view_func)


def instructor_required(view_func):
    return _role_required("instructor")(view_func)


def admin_required(view_func):
    return _role_required("admin", "super_admin")(view_func)


def super_admin_required(view_func):
    return _role_required("super_admin")(view_func)


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Class-based-view counterpart to the decorators above."""

    allowed_roles = ()

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.status != user.Status.ACTIVE:
            return False
        return user.role in self.allowed_roles


class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("student",)


class InstructorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("instructor",)


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("admin", "super_admin")


class SuperAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ("super_admin",)


def instructor_assignment_required(course_lookup="course"):
    """Ensures the logged-in instructor is actually assigned to the course
    referenced by the view's resolved object/kwargs before allowing access.
    Import-time circular deps are avoided by importing InstructorAssignment
    lazily inside the wrapped function.
    """

    def decorator(view_func):
        @wraps(view_func)
        @instructor_required
        def _wrapped(request, *args, **kwargs):
            from apps.instructors.models import InstructorAssignment

            course_id = kwargs.get(f"{course_lookup}_id") or kwargs.get(course_lookup)
            if not course_id:
                raise PermissionDenied("Course context is required.")
            is_assigned = InstructorAssignment.objects.filter(
                instructor=request.user,
                course_id=course_id,
                status=InstructorAssignment.Status.ACTIVE,
            ).exists()
            if not is_assigned:
                raise PermissionDenied("You are not assigned to this course.")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def enrollment_required(course_lookup="course"):
    """Ensures the logged-in student is actively enrolled in the course
    referenced by the view before allowing access to course content."""

    def decorator(view_func):
        @wraps(view_func)
        @student_required
        def _wrapped(request, *args, **kwargs):
            from apps.enrollments.models import Enrollment

            course_id = kwargs.get(f"{course_lookup}_id") or kwargs.get(course_lookup)
            if not course_id:
                raise PermissionDenied("Course context is required.")
            is_enrolled = Enrollment.objects.filter(
                student=request.user,
                course_id=course_id,
                status=Enrollment.Status.ACTIVE,
            ).exists()
            if not is_enrolled:
                raise PermissionDenied("You are not enrolled in this course.")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
