from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.courses.models import Course
from apps.instructors.models import InstructorAssignment

from .models import Question, QuestionOption


class QuestionBankAccessTests(TestCase):
    def setUp(self):
        self.course_a = Course.objects.create(
            title="Course A", slug="course-a", short_description="A", description="A",
            status=Course.Status.PUBLISHED,
        )
        self.course_b = Course.objects.create(
            title="Course B", slug="course-b", short_description="B", description="B",
            status=Course.Status.PUBLISHED,
        )
        self.instructor_a = User.objects.create_user(
            email="instructor_a@example.com", password="pass1234", full_name="Instructor A",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        self.instructor_b = User.objects.create_user(
            email="instructor_b@example.com", password="pass1234", full_name="Instructor B",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        InstructorAssignment.objects.create(instructor=self.instructor_a, course=self.course_a)
        InstructorAssignment.objects.create(instructor=self.instructor_b, course=self.course_b)

        self.question_b = Question.objects.create(
            course=self.course_b, question_type=Question.QuestionType.SHORT_ANSWER,
            question_text="A question only Instructor B owns.", status=Question.Status.PUBLISHED,
        )

    def test_instructor_cannot_edit_question_in_unassigned_course(self):
        self.client.login(username="instructor_a@example.com", password="pass1234")
        response = self.client.get(reverse("instructor_question_bank:edit", args=[self.question_b.id]))
        self.assertEqual(response.status_code, 404)

    def test_instructor_question_list_only_shows_assigned_course_questions(self):
        Question.objects.create(
            course=self.course_a, question_type=Question.QuestionType.SHORT_ANSWER,
            question_text="Instructor A's own question.", status=Question.Status.PUBLISHED,
        )
        self.client.login(username="instructor_a@example.com", password="pass1234")
        response = self.client.get(reverse("instructor_question_bank:list"))
        self.assertContains(response, "Instructor A&#x27;s own question.")
        self.assertNotContains(response, "A question only Instructor B owns.")

    def test_student_cannot_access_question_bank_at_all(self):
        student = User.objects.create_user(
            email="student@example.com", password="pass1234", full_name="Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.client.login(username="student@example.com", password="pass1234")
        response = self.client.get(reverse("instructor_question_bank:list"))
        self.assertEqual(response.status_code, 403)


class QuestionLockingTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Course", slug="course", short_description="C", description="C",
            status=Course.Status.PUBLISHED,
        )
        self.instructor = User.objects.create_user(
            email="instructor@example.com", password="pass1234", full_name="Instructor",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        InstructorAssignment.objects.create(instructor=self.instructor, course=self.course)
        self.question = Question.objects.create(
            course=self.course, question_type=Question.QuestionType.MULTIPLE_CHOICE,
            question_text="Locked question?", status=Question.Status.PUBLISHED,
        )
        QuestionOption.objects.create(question=self.question, option_text="Yes", is_correct=True, display_order=1)
        QuestionOption.objects.create(question=self.question, option_text="No", is_correct=False, display_order=2)

    def test_edit_blocked_once_question_is_locked(self):
        self.question.is_locked = True
        self.question.save()
        self.client.login(username="instructor@example.com", password="pass1234")
        response = self.client.get(
            reverse("instructor_question_bank:edit", args=[self.question.id]), follow=True
        )
        self.assertRedirects(
            response, reverse("instructor_question_bank:preview", args=[self.question.id])
        )
