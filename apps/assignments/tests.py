from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.instructors.models import InstructorAssignment

from .models import Assignment, AssignmentSubmission


class AssignmentWorkflowTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Course", slug="course", short_description="C", description="C",
            status=Course.Status.PUBLISHED,
        )
        self.instructor = User.objects.create_user(
            email="instructor@example.com", password="pass1234", full_name="Instructor",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        self.other_instructor = User.objects.create_user(
            email="other_instructor@example.com", password="pass1234", full_name="Other",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        InstructorAssignment.objects.create(instructor=self.instructor, course=self.course)

        self.student = User.objects.create_user(
            email="student@example.com", password="pass1234", full_name="Student A",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.student2 = User.objects.create_user(
            email="student2@example.com", password="pass1234", full_name="Student B",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        Enrollment.objects.create(student=self.student, course=self.course, status=Enrollment.Status.ACTIVE)
        # student2 intentionally NOT enrolled

        self.assignment = Assignment.objects.create(
            course=self.course, title="Essay", max_points=100, status=Assignment.Status.PUBLISHED,
        )

    def test_non_enrolled_student_cannot_access_assignment(self):
        self.client.login(username="student2@example.com", password="pass1234")
        response = self.client.get(reverse("student_assignments:detail", args=[self.assignment.id]))
        self.assertEqual(response.status_code, 404)

    def test_enrolled_student_can_submit_and_instructor_can_grade(self):
        self.client.login(username="student@example.com", password="pass1234")
        response = self.client.post(
            reverse("student_assignments:detail", args=[self.assignment.id]),
            {"text_submission": "My essay text."},
        )
        self.assertEqual(response.status_code, 302)
        submission = AssignmentSubmission.objects.get(assignment=self.assignment, student=self.student)
        self.assertEqual(submission.text_submission, "My essay text.")

        self.client.logout()
        self.client.login(username="instructor@example.com", password="pass1234")
        response = self.client.post(
            reverse("instructor_assignments:grade", args=[self.assignment.id, submission.id]),
            {"score": "88", "instructor_feedback": "Well done."},
        )
        self.assertEqual(response.status_code, 302)
        submission.refresh_from_db()
        self.assertEqual(submission.score, 88)
        self.assertEqual(submission.status, AssignmentSubmission.Status.GRADED)

    def test_score_cannot_exceed_max_points(self):
        submission = AssignmentSubmission.objects.create(
            assignment=self.assignment, student=self.student, text_submission="Text",
        )
        self.client.login(username="instructor@example.com", password="pass1234")
        response = self.client.post(
            reverse("instructor_assignments:grade", args=[self.assignment.id, submission.id]),
            {"score": "500", "instructor_feedback": "Too high."},
        )
        self.assertEqual(response.status_code, 200)  # form re-rendered with error, no redirect
        submission.refresh_from_db()
        self.assertIsNone(submission.score)

    def test_student_b_cannot_access_student_as_private_submission(self):
        """Student B must never be able to view Student A's assignment
        submission — even if enrolled in the same course."""
        Enrollment.objects.create(student=self.student2, course=self.course, status=Enrollment.Status.ACTIVE)
        submission = AssignmentSubmission.objects.create(
            assignment=self.assignment, student=self.student, text_submission="Private text.",
        )
        self.client.login(username="student2@example.com", password="pass1234")
        response = self.client.get(reverse("student_assignments:detail", args=[self.assignment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Private text.")

    def test_instructor_cannot_grade_submission_for_unassigned_course(self):
        submission = AssignmentSubmission.objects.create(
            assignment=self.assignment, student=self.student, text_submission="Text",
        )
        self.client.login(username="other_instructor@example.com", password="pass1234")
        response = self.client.get(
            reverse("instructor_assignments:grade", args=[self.assignment.id, submission.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_duplicate_submission_updates_rather_than_duplicates(self):
        self.client.login(username="student@example.com", password="pass1234")
        self.client.post(
            reverse("student_assignments:detail", args=[self.assignment.id]),
            {"text_submission": "First version."},
        )
        self.client.post(
            reverse("student_assignments:detail", args=[self.assignment.id]),
            {"text_submission": "Second version."},
        )
        self.assertEqual(
            AssignmentSubmission.objects.filter(assignment=self.assignment, student=self.student).count(), 1
        )
        submission = AssignmentSubmission.objects.get(assignment=self.assignment, student=self.student)
        self.assertEqual(submission.text_submission, "Second version.")

    def test_graded_submission_cannot_be_resubmitted_when_disallowed(self):
        self.assignment.allow_resubmission = False
        self.assignment.save()
        submission = AssignmentSubmission.objects.create(
            assignment=self.assignment, student=self.student, text_submission="Text",
            status=AssignmentSubmission.Status.GRADED, score=90,
        )
        self.client.login(username="student@example.com", password="pass1234")
        response = self.client.post(
            reverse("student_assignments:detail", args=[self.assignment.id]),
            {"text_submission": "Trying to resubmit."},
        )
        self.assertEqual(response.status_code, 302)
        submission.refresh_from_db()
        self.assertEqual(submission.text_submission, "Text")
