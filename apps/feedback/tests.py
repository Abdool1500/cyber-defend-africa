from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.instructors.models import InstructorAssignment

from .models import StudentFeedback


class FeedbackWorkflowTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Alpha Course", slug="alpha-course", short_description="A", description="A",
            status=Course.Status.PUBLISHED,
        )
        self.other_course = Course.objects.create(
            title="Zeta Course", slug="zeta-course", short_description="Z", description="Z",
            status=Course.Status.PUBLISHED,
        )
        self.instructor = User.objects.create_user(
            email="instructor@example.com", password="pass1234", full_name="Instructor",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        self.other_instructor = User.objects.create_user(
            email="other_instructor@example.com", password="pass1234", full_name="Other Instructor",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        InstructorAssignment.objects.create(instructor=self.instructor, course=self.course)
        InstructorAssignment.objects.create(instructor=self.other_instructor, course=self.other_course)

        self.student = User.objects.create_user(
            email="student@example.com", password="pass1234", full_name="Real Student Name",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        Enrollment.objects.create(student=self.student, course=self.course, status=Enrollment.Status.ACTIVE)

    def _valid_payload(self, **overrides):
        payload = {
            "overall_rating": "5", "content_quality": "4", "practical_lab_quality": "5",
            "platform_experience": "4", "difficulty": "3", "confidence_before": "2",
            "confidence_after": "5", "nps_score": "9", "most_helpful": "Labs",
            "improvement_suggestions": "", "additional_comments": "",
        }
        payload.update(overrides)
        return payload

    def _valid_model_kwargs(self, **overrides):
        kwargs = {
            "overall_rating": 5, "content_quality": 5, "practical_lab_quality": 5,
            "platform_experience": 5, "difficulty": 3, "confidence_before": 2,
            "confidence_after": 5, "nps_score": 9,
        }
        kwargs.update(overrides)
        return kwargs

    def test_only_enrolled_courses_are_eligible(self):
        self.client.login(username="student@example.com", password="pass1234")
        response = self.client.get(reverse("student_feedback:list"))
        self.assertContains(response, self.course.title)
        self.assertNotContains(response, self.other_course.title)

    def test_student_cannot_submit_feedback_for_unenrolled_course(self):
        self.client.login(username="student@example.com", password="pass1234")
        response = self.client.post(
            reverse("student_feedback:create", args=[self.other_course.id]), self._valid_payload()
        )
        self.assertEqual(response.status_code, 404)

    def test_rating_outside_1_to_5_is_rejected(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                StudentFeedback.objects.create(
                    student=self.student, course=self.course,
                    **self._valid_model_kwargs(overall_rating=6),
                )

    def test_duplicate_feedback_is_blocked(self):
        self.client.login(username="student@example.com", password="pass1234")
        self.client.post(reverse("student_feedback:create", args=[self.course.id]), self._valid_payload())
        self.client.post(
            reverse("student_feedback:create", args=[self.course.id]),
            self._valid_payload(overall_rating="1"),
        )
        self.assertEqual(
            StudentFeedback.objects.filter(student=self.student, course=self.course).count(), 1
        )
        # The first (rating 5), not the second, must be the one on record.
        self.assertEqual(
            StudentFeedback.objects.get(student=self.student, course=self.course).overall_rating, 5
        )

    def test_anonymous_feedback_hides_identity_in_instructor_view(self):
        StudentFeedback.objects.create(
            student=self.student, course=self.course, is_anonymous=True, **self._valid_model_kwargs(),
        )
        self.client.login(username="instructor@example.com", password="pass1234")
        response = self.client.get(reverse("instructor_feedback:list"))
        self.assertContains(response, "Anonymous Student")
        self.assertNotContains(response, "Real Student Name")

    def test_anonymous_feedback_hides_identity_in_csv_export(self):
        StudentFeedback.objects.create(
            student=self.student, course=self.course, is_anonymous=True, **self._valid_model_kwargs(),
        )
        self.client.login(username="instructor@example.com", password="pass1234")
        response = self.client.get(reverse("instructor_feedback:export_csv"))
        content = response.content.decode()
        self.assertIn("Anonymous Student", content)
        self.assertNotIn("Real Student Name", content)

    def test_instructor_cannot_see_feedback_for_unassigned_course(self):
        StudentFeedback.objects.create(
            student=self.student, course=self.course, **self._valid_model_kwargs(),
        )
        self.client.login(username="other_instructor@example.com", password="pass1234")
        response = self.client.get(reverse("instructor_feedback:list"))
        self.assertNotContains(response, "Real Student Name")
        self.assertNotContains(response, str(self.course.title))
