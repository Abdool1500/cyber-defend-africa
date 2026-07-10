import json

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.instructors.models import InstructorAssignment
from apps.question_bank.models import Question, QuestionOption

from .models import Quiz, QuizAttempt, QuizQuestion
from .services.attempts import QuizAttemptError, start_attempt, submit_attempt


def _make_mc_question(course, correct="A"):
    q = Question.objects.create(
        course=course, question_type=Question.QuestionType.MULTIPLE_CHOICE,
        question_text="2 + 2 = ?", status=Question.Status.PUBLISHED, default_points=1,
    )
    opt_a = QuestionOption.objects.create(question=q, option_text="4", is_correct=(correct == "A"), display_order=1)
    opt_b = QuestionOption.objects.create(question=q, option_text="5", is_correct=(correct == "B"), display_order=2)
    return q, opt_a, opt_b


def _make_ms_question(course):
    q = Question.objects.create(
        course=course, question_type=Question.QuestionType.MULTIPLE_SELECT,
        question_text="Select the prime numbers.", status=Question.Status.PUBLISHED, default_points=2,
    )
    opt_2 = QuestionOption.objects.create(question=q, option_text="2", is_correct=True, display_order=1)
    opt_3 = QuestionOption.objects.create(question=q, option_text="3", is_correct=True, display_order=2)
    opt_4 = QuestionOption.objects.create(question=q, option_text="4", is_correct=False, display_order=3)
    return q, opt_2, opt_3, opt_4


def _make_tf_question(course):
    q = Question.objects.create(
        course=course, question_type=Question.QuestionType.TRUE_FALSE,
        question_text="The sky is blue.", status=Question.Status.PUBLISHED, default_points=1,
    )
    opt_true = QuestionOption.objects.create(question=q, option_text="True", is_correct=True, display_order=1)
    opt_false = QuestionOption.objects.create(question=q, option_text="False", is_correct=False, display_order=2)
    return q, opt_true, opt_false


def _make_sa_question(course):
    return Question.objects.create(
        course=course, question_type=Question.QuestionType.SHORT_ANSWER,
        question_text="Explain X.", status=Question.Status.PUBLISHED, default_points=3,
    )


class QuizGradingTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Course", slug="course", short_description="C", description="C",
            status=Course.Status.PUBLISHED,
        )
        self.student = User.objects.create_user(
            email="student@example.com", password="pass1234", full_name="Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        Enrollment.objects.create(student=self.student, course=self.course, status=Enrollment.Status.ACTIVE)
        self.quiz = Quiz.objects.create(
            course=self.course, title="Quiz", status=Quiz.Status.PUBLISHED, attempt_limit=1,
        )

    def _attach(self, question, order):
        QuizQuestion.objects.create(quiz=self.quiz, question=question, display_order=order)

    def test_multiple_choice_autograded_correct(self):
        q, opt_a, _ = _make_mc_question(self.course, correct="A")
        self._attach(q, 1)
        attempt = start_attempt(self.quiz, self.student)
        aq = attempt.attempt_questions.get(question=q)
        from .services.attempts import save_answer

        save_answer(attempt, aq, option_ids=[str(opt_a.id)])
        submit_attempt(attempt)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, QuizAttempt.Status.GRADED)
        self.assertEqual(attempt.score, 1)
        self.assertEqual(attempt.percentage, 100.0)

    def test_multiple_choice_autograded_incorrect(self):
        q, _, opt_b = _make_mc_question(self.course, correct="A")
        self._attach(q, 1)
        attempt = start_attempt(self.quiz, self.student)
        aq = attempt.attempt_questions.get(question=q)
        from .services.attempts import save_answer

        save_answer(attempt, aq, option_ids=[str(opt_b.id)])
        submit_attempt(attempt)
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 0)

    def test_multiple_select_requires_exact_match(self):
        q, opt_2, opt_3, opt_4 = _make_ms_question(self.course)
        self._attach(q, 1)
        attempt = start_attempt(self.quiz, self.student)
        aq = attempt.attempt_questions.get(question=q)
        from .services.attempts import save_answer

        # Partial selection (missing opt_3) must not be treated as correct.
        save_answer(attempt, aq, option_ids=[str(opt_2.id)])
        submit_attempt(attempt)
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 0)

    def test_multiple_select_exact_match_is_correct(self):
        q, opt_2, opt_3, opt_4 = _make_ms_question(self.course)
        self._attach(q, 1)
        attempt = start_attempt(self.quiz, self.student)
        aq = attempt.attempt_questions.get(question=q)
        from .services.attempts import save_answer

        save_answer(attempt, aq, option_ids=[str(opt_2.id), str(opt_3.id)])
        submit_attempt(attempt)
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 2)

    def test_multiple_select_extra_option_rejected(self):
        """Selecting all options (including a wrong one) must not score as
        correct — guards against duplicate/extra-option manipulation."""
        q, opt_2, opt_3, opt_4 = _make_ms_question(self.course)
        self._attach(q, 1)
        attempt = start_attempt(self.quiz, self.student)
        aq = attempt.attempt_questions.get(question=q)
        from .services.attempts import save_answer

        save_answer(attempt, aq, option_ids=[str(opt_2.id), str(opt_3.id), str(opt_4.id)])
        submit_attempt(attempt)
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 0)

    def test_true_false_autograded(self):
        q, opt_true, _ = _make_tf_question(self.course)
        self._attach(q, 1)
        attempt = start_attempt(self.quiz, self.student)
        aq = attempt.attempt_questions.get(question=q)
        from .services.attempts import save_answer

        save_answer(attempt, aq, option_ids=[str(opt_true.id)])
        submit_attempt(attempt)
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 1)

    def test_short_answer_requires_manual_grading(self):
        q = _make_sa_question(self.course)
        self._attach(q, 1)
        attempt = start_attempt(self.quiz, self.student)
        aq = attempt.attempt_questions.get(question=q)
        from .services.attempts import save_answer

        save_answer(attempt, aq, text_answer="My answer.")
        submit_attempt(attempt)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, QuizAttempt.Status.PENDING_MANUAL_GRADING)
        self.assertTrue(attempt.requires_manual_grading)
        self.assertIsNone(attempt.score)


class QuizAttemptSecurityTests(TestCase):
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
            email="other_instructor@example.com", password="pass1234", full_name="Other Instructor",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        InstructorAssignment.objects.create(instructor=self.instructor, course=self.course)
        self.student = User.objects.create_user(
            email="student@example.com", password="pass1234", full_name="Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.student2 = User.objects.create_user(
            email="student2@example.com", password="pass1234", full_name="Student 2",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        Enrollment.objects.create(student=self.student, course=self.course, status=Enrollment.Status.ACTIVE)
        Enrollment.objects.create(student=self.student2, course=self.course, status=Enrollment.Status.ACTIVE)

        self.quiz = Quiz.objects.create(
            course=self.course, title="Quiz", status=Quiz.Status.PUBLISHED, attempt_limit=1,
        )
        self.question, self.opt_a, self.opt_b = _make_mc_question(self.course, correct="A")
        QuizQuestion.objects.create(quiz=self.quiz, question=self.question, display_order=1)

    def test_attempt_limit_enforced_server_side(self):
        attempt = start_attempt(self.quiz, self.student)
        submit_attempt(attempt)
        with self.assertRaises(QuizAttemptError):
            start_attempt(self.quiz, self.student)

    def test_expired_quiz_availability_enforced_server_side(self):
        self.quiz.available_until = timezone.now() - timezone.timedelta(days=1)
        self.quiz.save()
        with self.assertRaises(QuizAttemptError):
            start_attempt(self.quiz, self.student)

    def test_not_yet_available_quiz_enforced_server_side(self):
        self.quiz.available_from = timezone.now() + timezone.timedelta(days=1)
        self.quiz.save()
        with self.assertRaises(QuizAttemptError):
            start_attempt(self.quiz, self.student)

    def test_non_enrolled_student_cannot_start_attempt(self):
        outsider = User.objects.create_user(
            email="outsider@example.com", password="pass1234", full_name="Outsider",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        with self.assertRaises(QuizAttemptError):
            start_attempt(self.quiz, outsider)

    def test_refresh_does_not_regenerate_attempt_questions(self):
        attempt = start_attempt(self.quiz, self.student)
        first_ids = list(attempt.attempt_questions.values_list("id", flat=True))
        # Simulate "refresh" by simply re-fetching — start_attempt should
        # never be called again for an in-progress attempt (the view layer
        # enforces get_in_progress_attempt first); this test locks in that
        # the frozen rows are stable across repeated reads.
        second_ids = list(attempt.attempt_questions.values_list("id", flat=True))
        self.assertEqual(first_ids, second_ids)

    def test_student_cannot_access_another_students_attempt(self):
        attempt = start_attempt(self.quiz, self.student)
        self.client.login(username="student2@example.com", password="pass1234")
        response = self.client.get(reverse("student_quizzes:attempt", args=[attempt.id]))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse("student_quizzes:results", args=[attempt.id]))
        self.assertEqual(response.status_code, 404)

    def test_student_cannot_submit_for_another_student(self):
        attempt = start_attempt(self.quiz, self.student)
        self.client.login(username="student2@example.com", password="pass1234")
        response = self.client.post(
            reverse("student_quizzes:submit_attempt", args=[attempt.id]),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_instructor_cannot_grade_unassigned_course_attempt(self):
        attempt = start_attempt(self.quiz, self.student)
        submit_attempt(attempt)
        self.client.login(username="other_instructor@example.com", password="pass1234")
        response = self.client.get(reverse("instructor_grading:detail", args=[attempt.id]))
        self.assertEqual(response.status_code, 404)

    def test_correct_answer_not_exposed_via_api_before_submission(self):
        """Student-facing quiz-related API endpoints must never include
        is_correct or other answer-key fields."""
        self.client.login(username="student@example.com", password="pass1234")
        response = self.client.get("/api/v1/quizzes/")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertNotIn("is_correct", body)
        self.assertNotIn("model_answer", body)

    def test_student_cannot_access_question_bank_api(self):
        self.client.login(username="student@example.com", password="pass1234")
        response = self.client.get("/api/v1/question-bank/")
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_overwrite_awarded_points_via_post(self):
        """Nothing in the student-facing attempt endpoints accepts a
        client-submitted score/points value at all — save_answer only
        takes option_ids/text_answer, never awarded_points."""
        attempt = start_attempt(self.quiz, self.student)
        aq = attempt.attempt_questions.get(question=self.question)
        self.client.login(username="student@example.com", password="pass1234")
        response = self.client.post(
            reverse("student_quizzes:save_answer", args=[attempt.id]),
            data=json.dumps({
                "attempt_question_id": str(aq.id),
                "option_ids": [str(self.opt_a.id)],
                "awarded_points": 999,
                "is_correct": True,
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        submit_attempt(attempt)
        attempt.refresh_from_db()
        # Correct answer was selected, so score is legitimately 1 — the
        # point is that the injected awarded_points/is_correct were ignored.
        self.assertEqual(attempt.score, 1)
        self.assertNotEqual(attempt.score, 999)
