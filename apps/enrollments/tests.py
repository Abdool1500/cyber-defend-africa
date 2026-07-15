import json
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.analytics.models import LearningTimeEntry
from apps.courses.models import Course, CourseModule, Lesson

from .models import Enrollment, LessonProgress
from .student_views import MAX_HEARTBEAT_SECONDS


class LessonHeartbeatTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="heartbeat@example.com", password="pass1234", full_name="Heartbeat Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.course = Course.objects.create(
            title="Heartbeat Course", slug="heartbeat-course", short_description="x", description="x",
            status=Course.Status.PUBLISHED,
        )
        module = CourseModule.objects.create(course=self.course, title="Module 1", status="published")
        self.lesson = Lesson.objects.create(
            module=module, title="Lesson 1", slug="lesson-1", lesson_type=Lesson.LessonType.VIDEO,
            status="published",
        )
        Enrollment.objects.create(student=self.student, course=self.course, status=Enrollment.Status.ACTIVE)
        self.client.login(username="heartbeat@example.com", password="pass1234")

    def _heartbeat(self, seconds):
        url = reverse("student_learning:lesson_heartbeat", args=[self.course.id, self.lesson.id])
        return self.client.post(url, data=json.dumps({"seconds": seconds}), content_type="application/json")

    def test_heartbeat_creates_time_entry_for_today(self):
        response = self._heartbeat(60)
        self.assertEqual(response.status_code, 200)
        entry = LearningTimeEntry.objects.get(student=self.student, lesson=self.lesson)
        self.assertEqual(entry.date, timezone.localdate())
        self.assertEqual(entry.seconds, 60)

    def test_repeated_heartbeats_accumulate_same_day(self):
        self._heartbeat(60)
        self._heartbeat(60)
        self._heartbeat(45)
        entry = LearningTimeEntry.objects.get(student=self.student, lesson=self.lesson)
        self.assertEqual(entry.seconds, 165)
        self.assertEqual(
            LearningTimeEntry.objects.filter(student=self.student, lesson=self.lesson).count(), 1,
        )

    def test_oversized_seconds_value_is_capped(self):
        self._heartbeat(999999)
        entry = LearningTimeEntry.objects.get(student=self.student, lesson=self.lesson)
        self.assertEqual(entry.seconds, MAX_HEARTBEAT_SECONDS)

    def test_negative_seconds_value_is_ignored(self):
        response = self._heartbeat(-100)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(LearningTimeEntry.objects.filter(student=self.student, lesson=self.lesson).exists())

    def test_malformed_body_does_not_crash(self):
        url = reverse("student_learning:lesson_heartbeat", args=[self.course.id, self.lesson.id])
        response = self.client.post(url, data="not json", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(LearningTimeEntry.objects.filter(student=self.student, lesson=self.lesson).exists())

    def test_get_request_rejected(self):
        url = reverse("student_learning:lesson_heartbeat", args=[self.course.id, self.lesson.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_requires_active_enrollment(self):
        other_course = Course.objects.create(
            title="Other Course", slug="other-hb-course", short_description="x", description="x",
            status=Course.Status.PUBLISHED,
        )
        other_module = CourseModule.objects.create(course=other_course, title="M", status="published")
        other_lesson = Lesson.objects.create(
            module=other_module, title="L", slug="l", status="published",
        )
        url = reverse("student_learning:lesson_heartbeat", args=[other_course.id, other_lesson.id])
        response = self.client.post(url, data=json.dumps({"seconds": 60}), content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_redirected_to_login(self):
        self.client.logout()
        url = reverse("student_learning:lesson_heartbeat", args=[self.course.id, self.lesson.id])
        response = self.client.post(url, data=json.dumps({"seconds": 60}), content_type="application/json")
        self.assertEqual(response.status_code, 302)

    def test_different_days_create_separate_entries(self):
        import datetime
        from unittest.mock import patch

        self._heartbeat(60)
        tomorrow = timezone.localdate() + datetime.timedelta(days=1)
        with patch("django.utils.timezone.localdate", return_value=tomorrow):
            self._heartbeat(90)
        self.assertEqual(
            LearningTimeEntry.objects.filter(student=self.student, lesson=self.lesson).count(), 2,
        )


class ProgressAutoRecalculationTests(TestCase):
    """Enrollment.progress_percentage must stay correct automatically —
    via apps.enrollments.signals — regardless of which code path
    touches the underlying data (not just the one view that used to be
    the only caller of recalculate_progress())."""

    def setUp(self):
        self.student = User.objects.create_user(
            email="progress@example.com", password="pass1234", full_name="Progress Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.course = Course.objects.create(
            title="Progress Course", slug="progress-course", short_description="x", description="x",
            status=Course.Status.PUBLISHED,
        )
        self.module = CourseModule.objects.create(course=self.course, title="Module 1", status="published")
        self.lesson1 = Lesson.objects.create(module=self.module, title="L1", slug="l1", status="published")
        self.lesson2 = Lesson.objects.create(module=self.module, title="L2", slug="l2", status="published")
        self.enrollment = Enrollment.objects.create(
            student=self.student, course=self.course, status=Enrollment.Status.ACTIVE,
        )

    def test_creating_completed_lesson_progress_directly_recalculates(self):
        """Simulates a path that bypasses the lesson_detail view entirely
        (e.g. Django Admin, a future API, a data migration)."""
        self.assertEqual(self.enrollment.progress_percentage, 0)
        LessonProgress.objects.create(
            student=self.student, lesson=self.lesson1, completed=True, completed_at=timezone.now(),
        )
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 50)

    def test_deleting_lesson_progress_recalculates(self):
        progress = LessonProgress.objects.create(
            student=self.student, lesson=self.lesson1, completed=True, completed_at=timezone.now(),
        )
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 50)

        progress.delete()
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 0)

    def test_publishing_a_new_lesson_drops_existing_percentage(self):
        LessonProgress.objects.create(
            student=self.student, lesson=self.lesson1, completed=True, completed_at=timezone.now(),
        )
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 50)

        # A 3rd lesson gets published — same 1 completed lesson, now out
        # of 3, not 2. Every enrolled student's percentage must drop
        # automatically, without them touching anything themselves.
        Lesson.objects.create(module=self.module, title="L3", slug="l3", status="published")
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 33)

    def test_unpublishing_a_lesson_raises_percentage(self):
        LessonProgress.objects.create(
            student=self.student, lesson=self.lesson1, completed=True, completed_at=timezone.now(),
        )
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 50)

        self.lesson2.status = "draft"
        self.lesson2.save()
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 100)

    def test_unpublishing_a_module_recalculates_all_its_enrollments(self):
        other_student = User.objects.create_user(
            email="progress2@example.com", password="pass1234", full_name="Progress Student 2",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        other_enrollment = Enrollment.objects.create(
            student=other_student, course=self.course, status=Enrollment.Status.ACTIVE,
        )
        LessonProgress.objects.create(
            student=other_student, lesson=self.lesson1, completed=True, completed_at=timezone.now(),
        )
        other_enrollment.refresh_from_db()
        self.assertEqual(other_enrollment.progress_percentage, 50)

        second_module = CourseModule.objects.create(
            course=self.course, title="Module 2", status="published", display_order=1,
        )
        Lesson.objects.create(module=second_module, title="L4", slug="l4", status="published")
        other_enrollment.refresh_from_db()
        self.assertEqual(other_enrollment.progress_percentage, 33)  # 1 of 3 now

        second_module.status = "draft"
        second_module.save()
        other_enrollment.refresh_from_db()
        self.assertEqual(other_enrollment.progress_percentage, 50)  # back to 1 of 2


class ProgressAutoCompletionTests(TestCase):
    """16.Q data-quality fix: before this, nothing in the application
    ever set Enrollment.status to COMPLETED — every completion-rate/
    dropout-rate figure across the Phase 16 analytics services was
    silently undercounting completions, since nothing but a manual
    Django Admin edit could produce a COMPLETED enrollment."""

    def setUp(self):
        self.student = User.objects.create_user(
            email="autocomplete@example.com", password="pass1234", full_name="Auto Complete Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.course = Course.objects.create(
            title="Auto Complete Course", slug="auto-complete-course", short_description="x", description="x",
            status=Course.Status.PUBLISHED,
        )
        self.module = CourseModule.objects.create(course=self.course, title="Module 1", status="published")
        self.lesson = Lesson.objects.create(module=self.module, title="L1", slug="l1", status="published")
        self.enrollment = Enrollment.objects.create(
            student=self.student, course=self.course, status=Enrollment.Status.ACTIVE,
        )

    def test_reaching_100_percent_auto_completes_the_enrollment(self):
        LessonProgress.objects.create(
            student=self.student, lesson=self.lesson, completed=True, completed_at=timezone.now(),
        )
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 100)
        self.assertEqual(self.enrollment.status, Enrollment.Status.COMPLETED)
        self.assertIsNotNone(self.enrollment.completed_at)

    def test_below_100_percent_never_auto_completes(self):
        Lesson.objects.create(module=self.module, title="L2", slug="l2", status="published")
        LessonProgress.objects.create(
            student=self.student, lesson=self.lesson, completed=True, completed_at=timezone.now(),
        )
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 50)
        self.assertEqual(self.enrollment.status, Enrollment.Status.ACTIVE)

    def test_completed_enrollment_is_frozen_from_course_structure_recalculation(self):
        """Once COMPLETED, publishing a new lesson in the course doesn't
        even touch this enrollment — apps.enrollments.signals'
        _recalculate_for_all_enrollments() only ever recalculates ACTIVE
        enrollments, so a completed enrollment's progress/status are
        left exactly as they were when the student finished."""
        LessonProgress.objects.create(
            student=self.student, lesson=self.lesson, completed=True, completed_at=timezone.now(),
        )
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, Enrollment.Status.COMPLETED)

        Lesson.objects.create(module=self.module, title="L2", slug="l2", status="published")
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 100)
        self.assertEqual(self.enrollment.status, Enrollment.Status.COMPLETED)

    def test_recalculate_progress_itself_never_demotes_completed_status(self):
        """Directly exercises the guard inside recalculate_progress() —
        not just the fact that the signal path happens to filter by
        ACTIVE — in case a future caller (API, admin action, management
        command) calls recalculate_progress() directly on a completed
        enrollment."""
        LessonProgress.objects.create(
            student=self.student, lesson=self.lesson, completed=True, completed_at=timezone.now(),
        )
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, Enrollment.Status.COMPLETED)

        Lesson.objects.create(module=self.module, title="L2", slug="l2", status="published")
        self.enrollment.recalculate_progress()
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 50)
        self.assertEqual(self.enrollment.status, Enrollment.Status.COMPLETED)

    def test_withdrawn_enrollment_never_auto_completes(self):
        self.enrollment.status = Enrollment.Status.WITHDRAWN
        self.enrollment.save(update_fields=["status"])
        LessonProgress.objects.create(
            student=self.student, lesson=self.lesson, completed=True, completed_at=timezone.now(),
        )
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 100)
        self.assertEqual(self.enrollment.status, Enrollment.Status.WITHDRAWN)


class BackfillEnrollmentCompletionCommandTests(TestCase):
    """16.Q: a one-off backfill for any enrollment that reached 100%
    progress before the auto-completion fix shipped."""

    def setUp(self):
        self.student = User.objects.create_user(
            email="backfillcmdstudent@example.com", password="pass1234", full_name="Backfill Cmd Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.course = Course.objects.create(
            title="Backfill Cmd Course", slug="backfill-cmd-course", short_description="x", description="x",
            status=Course.Status.PUBLISHED,
        )
        self.module = CourseModule.objects.create(course=self.course, title="M1", status="published")
        self.lesson = Lesson.objects.create(module=self.module, title="L1", slug="l1", status="published")

    def _make_stale_completed_enrollment(self):
        enrollment = Enrollment.objects.create(
            student=self.student, course=self.course, status=Enrollment.Status.ACTIVE,
        )
        LessonProgress.objects.create(
            student=self.student, lesson=self.lesson, completed=True, completed_at=timezone.now(),
        )
        # The signal already promotes this correctly under current code —
        # force it back to ACTIVE to simulate a row written before the fix.
        Enrollment.objects.filter(pk=enrollment.pk).update(status=Enrollment.Status.ACTIVE, completed_at=None)
        enrollment.refresh_from_db()
        return enrollment

    def test_backfill_promotes_stale_100_percent_enrollment(self):
        enrollment = self._make_stale_completed_enrollment()
        call_command("backfill_enrollment_completion", stdout=StringIO())
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, Enrollment.Status.COMPLETED)
        self.assertIsNotNone(enrollment.completed_at)

    def test_dry_run_reports_but_does_not_save(self):
        enrollment = self._make_stale_completed_enrollment()
        out = StringIO()
        call_command("backfill_enrollment_completion", "--dry-run", stdout=out)
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, Enrollment.Status.ACTIVE)
        self.assertIn("1 of 1", out.getvalue())

    def test_below_100_percent_enrollment_is_untouched(self):
        Lesson.objects.create(module=self.module, title="L2", slug="l2", status="published")
        enrollment = Enrollment.objects.create(
            student=self.student, course=self.course, status=Enrollment.Status.ACTIVE,
        )
        LessonProgress.objects.create(
            student=self.student, lesson=self.lesson, completed=True, completed_at=timezone.now(),
        )
        call_command("backfill_enrollment_completion", stdout=StringIO())
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, Enrollment.Status.ACTIVE)
