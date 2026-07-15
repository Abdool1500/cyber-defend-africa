from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.instructors.models import InstructorAssignment

from .models import LabProgress, PracticalLab


def _make_course(slug="labs-course"):
    return Course.objects.create(
        title="Labs Course", slug=slug, short_description="x", description="x", status=Course.Status.PUBLISHED,
    )


def _make_lab(course, category=PracticalLab.Category.NMAP, status=PracticalLab.Status.PUBLISHED, **kwargs):
    return PracticalLab.objects.create(
        course=course, title="Nmap Scanning Basics", category=category, status=status, **kwargs
    )


class LabProgressModelTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="labmodel@example.com", password="pass1234", full_name="Lab Model",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.course = _make_course()
        self.lab = _make_lab(self.course)

    def test_cannot_create_duplicate_progress_for_same_student_lab(self):
        LabProgress.objects.create(lab=self.lab, student=self.student)
        with self.assertRaises(Exception):
            LabProgress.objects.create(lab=self.lab, student=self.student)

    def test_completion_duration_none_until_completed(self):
        progress = LabProgress.objects.create(lab=self.lab, student=self.student)
        self.assertIsNone(progress.completion_duration)
        progress.completed_at = timezone.now()
        progress.save()
        self.assertIsNotNone(progress.completion_duration)

    def test_is_graded_reflects_score_presence(self):
        progress = LabProgress.objects.create(lab=self.lab, student=self.student)
        self.assertFalse(progress.is_graded)
        progress.score = 80
        progress.save()
        self.assertTrue(progress.is_graded)


class StudentLabFlowTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="labstudent@example.com", password="pass1234", full_name="Lab Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.course = _make_course()
        self.lab = _make_lab(self.course)
        Enrollment.objects.create(student=self.student, course=self.course, status=Enrollment.Status.ACTIVE)
        self.client.login(username="labstudent@example.com", password="pass1234")

    def _post_action(self, action):
        url = reverse("student_labs:detail", args=[self.lab.id])
        return self.client.post(url, {"action": action})

    def test_lab_list_shows_not_started_when_no_progress(self):
        response = self.client.get(reverse("student_labs:list"))
        self.assertContains(response, "Not Started")

    def test_start_lab_creates_in_progress_record(self):
        self._post_action("start")
        progress = LabProgress.objects.get(lab=self.lab, student=self.student)
        self.assertEqual(progress.status, LabProgress.Status.IN_PROGRESS)
        self.assertEqual(progress.attempts, 1)

    def test_mark_complete_sets_completed_status_and_timestamp(self):
        self._post_action("start")
        self._post_action("complete")
        progress = LabProgress.objects.get(lab=self.lab, student=self.student)
        self.assertEqual(progress.status, LabProgress.Status.COMPLETED)
        self.assertIsNotNone(progress.completed_at)

    def test_restart_increments_attempts_and_reopens(self):
        self._post_action("start")
        self._post_action("complete")
        self._post_action("restart")
        progress = LabProgress.objects.get(lab=self.lab, student=self.student)
        self.assertEqual(progress.status, LabProgress.Status.IN_PROGRESS)
        self.assertEqual(progress.attempts, 2)
        self.assertIsNone(progress.completed_at)

    def test_cannot_restart_once_graded(self):
        self._post_action("start")
        self._post_action("complete")
        progress = LabProgress.objects.get(lab=self.lab, student=self.student)
        progress.score = 90
        progress.save()

        self._post_action("restart")
        progress.refresh_from_db()
        self.assertEqual(progress.status, LabProgress.Status.COMPLETED)
        self.assertEqual(progress.attempts, 1)

    def test_cannot_restart_when_resubmission_disabled(self):
        self.lab.allow_resubmission = False
        self.lab.save()
        self._post_action("start")
        self._post_action("complete")

        self._post_action("restart")
        progress = LabProgress.objects.get(lab=self.lab, student=self.student)
        self.assertEqual(progress.status, LabProgress.Status.COMPLETED)
        self.assertEqual(progress.attempts, 1)

    def test_unenrolled_student_cannot_access_lab(self):
        other_course = _make_course(slug="other-labs-course")
        other_lab = _make_lab(other_course)
        response = self.client.get(reverse("student_labs:detail", args=[other_lab.id]))
        self.assertEqual(response.status_code, 404)

    def test_draft_lab_not_visible_to_students(self):
        draft_lab = _make_lab(self.course, status=PracticalLab.Status.DRAFT)
        response = self.client.get(reverse("student_labs:detail", args=[draft_lab.id]))
        self.assertEqual(response.status_code, 404)


class InstructorLabManagementTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            email="labinstructor@example.com", password="pass1234", full_name="Lab Instructor",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        self.other_instructor = User.objects.create_user(
            email="otherinstructor@example.com", password="pass1234", full_name="Other Instructor",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        self.course = _make_course()
        self.other_course = _make_course(slug="other-instructor-course")
        InstructorAssignment.objects.create(
            instructor=self.instructor, course=self.course, status=InstructorAssignment.Status.ACTIVE,
        )
        InstructorAssignment.objects.create(
            instructor=self.other_instructor, course=self.other_course, status=InstructorAssignment.Status.ACTIVE,
        )
        self.lab = _make_lab(self.course)
        self.client.login(username="labinstructor@example.com", password="pass1234")

    def test_lab_list_only_shows_own_assigned_courses(self):
        other_lab = _make_lab(self.other_course)
        response = self.client.get(reverse("instructor_labs:list"))
        self.assertContains(response, self.lab.title)
        # Same title text for both fixtures, so check course scoping via the queryset directly too.
        from .instructor_views import _assigned_course_ids
        self.assertNotIn(self.other_course.id, _assigned_course_ids(self.instructor))

    def test_create_lab_restricted_to_assigned_courses(self):
        response = self.client.post(reverse("instructor_labs:create"), {
            "course": self.other_course.id, "title": "Sneaky Lab", "category": PracticalLab.Category.LINUX,
            "max_score": 100, "status": PracticalLab.Status.DRAFT, "description": "", "instructions": "",
        })
        self.assertEqual(response.status_code, 200)  # form re-rendered with error, not a redirect
        self.assertFalse(PracticalLab.objects.filter(title="Sneaky Lab").exists())

    def test_cannot_edit_lab_from_unassigned_course(self):
        other_lab = _make_lab(self.other_course)
        response = self.client.get(reverse("instructor_labs:edit", args=[other_lab.id]))
        self.assertEqual(response.status_code, 404)

    def test_grade_lab_updates_score_and_logs_audit(self):
        student = User.objects.create_user(
            email="gradedstudent@example.com", password="pass1234", full_name="Graded Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        progress = LabProgress.objects.create(
            lab=self.lab, student=student, status=LabProgress.Status.COMPLETED, completed_at=timezone.now(),
        )
        response = self.client.post(
            reverse("instructor_labs:grade", args=[self.lab.id, progress.id]),
            {"score": 85, "instructor_feedback": "Solid work."},
        )
        self.assertEqual(response.status_code, 302)
        progress.refresh_from_db()
        self.assertEqual(progress.score, 85)
        self.assertEqual(progress.graded_by, self.instructor)
        self.assertTrue(AuditLog.objects.filter(action="lab_progress.grade", entity_id=str(progress.id)).exists())

    def test_score_cannot_exceed_max_score(self):
        student = User.objects.create_user(
            email="capstudent@example.com", password="pass1234", full_name="Cap Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        progress = LabProgress.objects.create(lab=self.lab, student=student)
        response = self.client.post(
            reverse("instructor_labs:grade", args=[self.lab.id, progress.id]),
            {"score": 9999, "instructor_feedback": ""},
        )
        self.assertContains(response, "cannot exceed the maximum")
        progress.refresh_from_db()
        self.assertIsNone(progress.score)

    def test_cannot_grade_progress_from_unassigned_course(self):
        student = User.objects.create_user(
            email="crossstudent@example.com", password="pass1234", full_name="Cross Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        other_lab = _make_lab(self.other_course)
        progress = LabProgress.objects.create(lab=other_lab, student=student)
        response = self.client.get(reverse("instructor_labs:grade", args=[other_lab.id, progress.id]))
        self.assertEqual(response.status_code, 404)
