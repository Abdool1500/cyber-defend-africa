import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.courses.models import Course, CourseModule, Lesson
from apps.quizzes.models import Quiz, QuizAttempt

from .models import LearningSession, LearningTimeEntry
from .services.cohort_stats import get_cohort_stats
from .services.course_progress import (
    get_course_module_breakdown,
    get_module_progress,
    get_overall_academy_progress,
)
from .services.impact_stats import get_impact_dashboard_data
from .services.lab_progress import get_lab_summary
from .services.fid_report import get_fid_impact_report_data
from .services.instructor_stats import get_instructor_dashboard_stats
from .services.leaderboard import get_leaderboard_position
from .services.learning_time import get_course_time_breakdown, get_learning_streak, get_learning_time_summary
from .services.platform_stats import get_platform_analytics
from .services.skill_improvement import get_skill_improvement


def _make_course(slug="ethical-hacking"):
    return Course.objects.create(
        title="Ethical Hacking", slug=slug, short_description="x", description="x",
        status=Course.Status.PUBLISHED,
    )


def _make_lesson(course, lesson_type=Lesson.LessonType.READING, slug="lesson-1"):
    # get_or_create so multiple lessons in the same test course share one
    # module, rather than colliding on CourseModule's unique
    # (course, display_order) constraint.
    module, _created = CourseModule.objects.get_or_create(
        course=course, title="Module 1", defaults={"status": "published"},
    )
    return Lesson.objects.create(
        module=module, title="Lesson", slug=slug, lesson_type=lesson_type, status="published",
    )


def _make_quiz(course, quiz_type, passing_score=70):
    return Quiz.objects.create(
        course=course, title=f"{quiz_type} quiz", status=Quiz.Status.PUBLISHED,
        quiz_type=quiz_type, passing_score=passing_score,
    )


def _make_graded_attempt(quiz, student, percentage, attempt_number=1):
    return QuizAttempt.objects.create(
        quiz=quiz, student=student, attempt_number=attempt_number,
        status=QuizAttempt.Status.GRADED, percentage=percentage,
        score=percentage, max_score=100, graded_at=timezone.now(),
    )


class SkillImprovementServiceTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="skillstudent@example.com", password="pass1234", full_name="Skill Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.course = _make_course()

    def test_no_pre_or_post_test_quiz_configured(self):
        result = get_skill_improvement(self.student, self.course)
        self.assertIsNone(result["pre_test_quiz"])
        self.assertIsNone(result["post_test_quiz"])
        self.assertFalse(result["complete"])
        self.assertIsNone(result["improvement"])

    def test_pre_test_exists_but_not_attempted(self):
        _make_quiz(self.course, Quiz.QuizType.PRE_TEST)
        result = get_skill_improvement(self.student, self.course)
        self.assertIsNotNone(result["pre_test_quiz"])
        self.assertIsNone(result["pre_test_percentage"])
        self.assertFalse(result["complete"])

    def test_full_improvement_calculation(self):
        pre_quiz = _make_quiz(self.course, Quiz.QuizType.PRE_TEST)
        post_quiz = _make_quiz(self.course, Quiz.QuizType.POST_TEST, passing_score=70)
        _make_graded_attempt(pre_quiz, self.student, 35.0)
        _make_graded_attempt(post_quiz, self.student, 90.0)

        result = get_skill_improvement(self.student, self.course)
        self.assertTrue(result["complete"])
        self.assertEqual(result["pre_test_percentage"], 35.0)
        self.assertEqual(result["post_test_percentage"], 90.0)
        self.assertEqual(result["improvement"], 55.0)
        # Normalized gain: (90-35)/(100-35)*100 = 84.62
        self.assertAlmostEqual(result["normalized_gain"], 84.62, places=1)
        self.assertTrue(result["passed_post_test"])

    def test_uses_latest_graded_attempt_not_first(self):
        pre_quiz = _make_quiz(self.course, Quiz.QuizType.PRE_TEST)
        post_quiz = _make_quiz(self.course, Quiz.QuizType.POST_TEST)
        _make_graded_attempt(pre_quiz, self.student, 35.0, attempt_number=1)
        _make_graded_attempt(post_quiz, self.student, 60.0, attempt_number=1)
        _make_graded_attempt(post_quiz, self.student, 88.0, attempt_number=2)

        result = get_skill_improvement(self.student, self.course)
        self.assertEqual(result["post_test_percentage"], 88.0)

    def test_ignores_ungraded_attempts(self):
        pre_quiz = _make_quiz(self.course, Quiz.QuizType.PRE_TEST)
        QuizAttempt.objects.create(
            quiz=pre_quiz, student=self.student, attempt_number=1,
            status=QuizAttempt.Status.IN_PROGRESS,
        )
        result = get_skill_improvement(self.student, self.course)
        self.assertIsNone(result["pre_test_percentage"])

    def test_perfect_pre_test_score_avoids_division_by_zero(self):
        pre_quiz = _make_quiz(self.course, Quiz.QuizType.PRE_TEST)
        post_quiz = _make_quiz(self.course, Quiz.QuizType.POST_TEST)
        _make_graded_attempt(pre_quiz, self.student, 100.0)
        _make_graded_attempt(post_quiz, self.student, 100.0)

        result = get_skill_improvement(self.student, self.course)
        self.assertEqual(result["improvement"], 0.0)
        self.assertEqual(result["normalized_gain"], 0.0)

    def test_failed_post_test_reflected_in_passed_flag(self):
        post_quiz = _make_quiz(self.course, Quiz.QuizType.POST_TEST, passing_score=70)
        _make_graded_attempt(post_quiz, self.student, 50.0)
        result = get_skill_improvement(self.student, self.course)
        self.assertFalse(result["passed_post_test"])


class QuizTypeConstraintTests(TestCase):
    """Backs up spec section 1: "Each course must support: Diagnostic
    Pre-Test, Final Post-Test" — singular, so more than one of each per
    course is a data-integrity error, not a valid configuration."""

    def setUp(self):
        self.course = _make_course()

    def test_cannot_create_two_pre_tests_for_same_course(self):
        _make_quiz(self.course, Quiz.QuizType.PRE_TEST)
        with self.assertRaises(Exception):
            _make_quiz(self.course, Quiz.QuizType.PRE_TEST)

    def test_multiple_standard_quizzes_are_allowed(self):
        _make_quiz(self.course, Quiz.QuizType.STANDARD)
        _make_quiz(self.course, Quiz.QuizType.STANDARD)  # should not raise

    def test_pre_and_post_test_can_coexist(self):
        _make_quiz(self.course, Quiz.QuizType.PRE_TEST)
        _make_quiz(self.course, Quiz.QuizType.POST_TEST)  # should not raise


class LearningTimeServiceTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="timestudent@example.com", password="pass1234", full_name="Time Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.course = _make_course(slug="time-course")
        self.video_lesson = _make_lesson(self.course, Lesson.LessonType.VIDEO, slug="video-lesson")
        self.reading_lesson = _make_lesson(self.course, Lesson.LessonType.READING, slug="reading-lesson")
        self.lab_lesson = _make_lesson(self.course, Lesson.LessonType.LAB, slug="lab-lesson")

    def test_no_time_logged_returns_zeros(self):
        summary = get_learning_time_summary(self.student)
        self.assertEqual(summary, {"today_seconds": 0, "week_seconds": 0, "month_seconds": 0, "lifetime_seconds": 0})

    def test_today_week_month_lifetime_boundaries(self):
        today = timezone.localdate()
        LearningTimeEntry.objects.create(student=self.student, lesson=self.video_lesson, date=today, seconds=100)
        # 3 days ago: counts toward week/month/lifetime but not "today"
        LearningTimeEntry.objects.create(
            student=self.student, lesson=self.video_lesson, date=today - datetime.timedelta(days=3), seconds=200,
        )
        # last month: counts toward lifetime only
        LearningTimeEntry.objects.create(
            student=self.student, lesson=self.video_lesson, date=today - datetime.timedelta(days=40), seconds=300,
        )

        summary = get_learning_time_summary(self.student)
        self.assertEqual(summary["today_seconds"], 100)
        # week/month totals depend on where "today" falls, but must always
        # include today's entry and never include the 40-day-old one in
        # anything except lifetime.
        self.assertGreaterEqual(summary["week_seconds"], 100)
        self.assertGreaterEqual(summary["month_seconds"], summary["week_seconds"])
        self.assertEqual(summary["lifetime_seconds"], 600)

    def test_lifetime_never_less_than_month_never_less_than_week_never_less_than_today(self):
        today = timezone.localdate()
        for days_ago, seconds in [(0, 50), (2, 60), (10, 70), (60, 80)]:
            LearningTimeEntry.objects.create(
                student=self.student, lesson=self.video_lesson, date=today - datetime.timedelta(days=days_ago),
                seconds=seconds,
            )
        summary = get_learning_time_summary(self.student)
        self.assertLessEqual(summary["today_seconds"], summary["week_seconds"])
        self.assertLessEqual(summary["week_seconds"], summary["month_seconds"])
        self.assertLessEqual(summary["month_seconds"], summary["lifetime_seconds"])

    def test_only_counts_this_students_time(self):
        other_student = User.objects.create_user(
            email="other@example.com", password="pass1234", full_name="Other",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        LearningTimeEntry.objects.create(
            student=other_student, lesson=self.video_lesson, date=timezone.localdate(), seconds=999,
        )
        summary = get_learning_time_summary(self.student)
        self.assertEqual(summary["today_seconds"], 0)

    def test_course_time_breakdown_by_lesson_type(self):
        today = timezone.localdate()
        LearningTimeEntry.objects.create(student=self.student, lesson=self.video_lesson, date=today, seconds=120)
        LearningTimeEntry.objects.create(student=self.student, lesson=self.reading_lesson, date=today, seconds=60)
        LearningTimeEntry.objects.create(student=self.student, lesson=self.lab_lesson, date=today, seconds=300)

        breakdown = get_course_time_breakdown(self.student, self.course)
        self.assertEqual(breakdown["total_seconds"], 480)
        self.assertEqual(breakdown["by_type"]["video"], 120)
        self.assertEqual(breakdown["by_type"]["reading"], 60)
        self.assertEqual(breakdown["by_type"]["lab"], 300)
        self.assertEqual(breakdown["by_type"]["live"], 0)

    def test_course_time_breakdown_excludes_other_courses(self):
        other_course = _make_course(slug="other-course")
        other_lesson = _make_lesson(other_course, Lesson.LessonType.VIDEO, slug="other-lesson")
        LearningTimeEntry.objects.create(
            student=self.student, lesson=other_lesson, date=timezone.localdate(), seconds=500,
        )
        breakdown = get_course_time_breakdown(self.student, self.course)
        self.assertEqual(breakdown["total_seconds"], 0)

    def test_streak_zero_with_no_entries(self):
        self.assertEqual(get_learning_streak(self.student)["current_streak"], 0)

    def test_streak_counts_consecutive_days_ending_today(self):
        today = timezone.localdate()
        for days_ago in range(4):
            LearningTimeEntry.objects.create(
                student=self.student, lesson=self.video_lesson, date=today - datetime.timedelta(days=days_ago),
                seconds=60,
            )
        self.assertEqual(get_learning_streak(self.student)["current_streak"], 4)

    def test_streak_survives_missing_entry_for_today_but_not_yesterday(self):
        today = timezone.localdate()
        LearningTimeEntry.objects.create(
            student=self.student, lesson=self.video_lesson, date=today - datetime.timedelta(days=1), seconds=60,
        )
        LearningTimeEntry.objects.create(
            student=self.student, lesson=self.video_lesson, date=today - datetime.timedelta(days=2), seconds=60,
        )
        self.assertEqual(get_learning_streak(self.student)["current_streak"], 2)

    def test_streak_broken_by_a_gap_day(self):
        today = timezone.localdate()
        LearningTimeEntry.objects.create(student=self.student, lesson=self.video_lesson, date=today, seconds=60)
        LearningTimeEntry.objects.create(
            student=self.student, lesson=self.video_lesson, date=today - datetime.timedelta(days=3), seconds=60,
        )
        self.assertEqual(get_learning_streak(self.student)["current_streak"], 1)


class LeaderboardServiceTests(TestCase):
    def _make_student(self, email):
        return User.objects.create_user(
            email=email, password="pass1234", full_name=email.split("@")[0],
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )

    def test_student_with_no_graded_attempts_is_not_ranked(self):
        student = self._make_student("unranked@example.com")
        result = get_leaderboard_position(student)
        self.assertFalse(result["eligible"])
        self.assertIsNone(result["top_percentage"])

    def test_best_scorer_is_top_of_ranking(self):
        course = _make_course(slug="leaderboard-course")
        quiz = Quiz.objects.create(course=course, title="LB Quiz", status=Quiz.Status.PUBLISHED)
        top_student = self._make_student("topscorer@example.com")
        low_student = self._make_student("lowscorer@example.com")
        QuizAttempt.objects.create(
            quiz=quiz, student=top_student, attempt_number=1, status=QuizAttempt.Status.GRADED,
            percentage=95.0, score=95, max_score=100, graded_at=timezone.now(),
        )
        QuizAttempt.objects.create(
            quiz=quiz, student=low_student, attempt_number=1, status=QuizAttempt.Status.GRADED,
            percentage=40.0, score=40, max_score=100, graded_at=timezone.now(),
        )

        top_result = get_leaderboard_position(top_student)
        self.assertTrue(top_result["eligible"])
        self.assertEqual(top_result["top_percentage"], 50)  # 1st of 2
        self.assertEqual(top_result["total_ranked"], 2)

        low_result = get_leaderboard_position(low_student)
        self.assertEqual(low_result["top_percentage"], 100)  # 2nd of 2


class LearningTimeEntryConstraintTests(TestCase):
    def test_unique_per_student_lesson_day(self):
        student = User.objects.create_user(
            email="constraint@example.com", password="pass1234", full_name="Constraint Test",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        course = _make_course(slug="constraint-course")
        lesson = _make_lesson(course, slug="constraint-lesson")
        today = timezone.localdate()
        LearningTimeEntry.objects.create(student=student, lesson=lesson, date=today, seconds=60)
        with self.assertRaises(Exception):
            LearningTimeEntry.objects.create(student=student, lesson=lesson, date=today, seconds=30)


class LearningSessionSignalTests(TestCase):
    """Uses the real Django test Client login()/logout(), which fires
    the actual user_logged_in/user_logged_out signals — not a
    reimplementation of the signal-dispatch mechanics."""

    def setUp(self):
        self.student = User.objects.create_user(
            email="sessiontest@example.com", password="pass1234", full_name="Session Test",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )

    def test_login_creates_open_session(self):
        self.assertEqual(LearningSession.objects.filter(user=self.student).count(), 0)
        self.client.login(username="sessiontest@example.com", password="pass1234")
        sessions = LearningSession.objects.filter(user=self.student)
        self.assertEqual(sessions.count(), 1)
        self.assertIsNone(sessions.first().ended_at)

    def test_logout_closes_the_open_session(self):
        self.client.login(username="sessiontest@example.com", password="pass1234")
        self.client.logout()
        session = LearningSession.objects.get(user=self.student)
        self.assertIsNotNone(session.ended_at)

    def test_login_again_closes_previous_stale_session(self):
        self.client.login(username="sessiontest@example.com", password="pass1234")
        first_session = LearningSession.objects.get(user=self.student)
        self.assertIsNone(first_session.ended_at)

        # Simulate the tab being closed without logout, then logging in
        # again later — the stale session must get capped/closed, not
        # left open forever.
        self.client.login(username="sessiontest@example.com", password="pass1234")
        first_session.refresh_from_db()
        self.assertIsNotNone(first_session.ended_at)
        self.assertEqual(LearningSession.objects.filter(user=self.student).count(), 2)

    def test_stale_session_capped_at_max_hours(self):
        from .signals import MAX_SESSION_HOURS

        self.client.login(username="sessiontest@example.com", password="pass1234")
        session = LearningSession.objects.get(user=self.student)
        # Backdate the session start far beyond the cap, as if it were
        # abandoned days ago.
        session.started_at = timezone.now() - datetime.timedelta(days=3)
        session.save(update_fields=["started_at"])

        self.client.login(username="sessiontest@example.com", password="pass1234")
        session.refresh_from_db()
        expected_end = session.started_at + datetime.timedelta(hours=MAX_SESSION_HOURS)
        self.assertAlmostEqual(
            session.ended_at.timestamp(), expected_end.timestamp(), delta=5,
        )


class LabSummaryServiceTests(TestCase):
    def setUp(self):
        from apps.enrollments.models import Enrollment
        from apps.labs.models import LabProgress, PracticalLab

        self.LabProgress = LabProgress
        self.PracticalLab = PracticalLab
        self.student = User.objects.create_user(
            email="labsummary@example.com", password="pass1234", full_name="Lab Summary",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.course = _make_course(slug="lab-summary-course")
        Enrollment.objects.create(student=self.student, course=self.course, status=Enrollment.Status.ACTIVE)

    def test_no_labs_returns_zeros(self):
        summary = get_lab_summary(self.student)
        self.assertEqual(summary, {"total": 0, "completed": 0, "in_progress": 0, "not_started": 0})

    def test_counts_by_status_including_not_started(self):
        lab1 = self.PracticalLab.objects.create(
            course=self.course, title="Lab 1", category=self.PracticalLab.Category.LINUX,
            status=self.PracticalLab.Status.PUBLISHED,
        )
        lab2 = self.PracticalLab.objects.create(
            course=self.course, title="Lab 2", category=self.PracticalLab.Category.NMAP,
            status=self.PracticalLab.Status.PUBLISHED,
        )
        self.PracticalLab.objects.create(
            course=self.course, title="Lab 3 (not started)", category=self.PracticalLab.Category.WIRESHARK,
            status=self.PracticalLab.Status.PUBLISHED,
        )
        self.LabProgress.objects.create(lab=lab1, student=self.student, status=self.LabProgress.Status.COMPLETED)
        self.LabProgress.objects.create(lab=lab2, student=self.student, status=self.LabProgress.Status.IN_PROGRESS)

        summary = get_lab_summary(self.student)
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["completed"], 1)
        self.assertEqual(summary["in_progress"], 1)
        self.assertEqual(summary["not_started"], 1)

    def test_draft_labs_excluded_from_total(self):
        self.PracticalLab.objects.create(
            course=self.course, title="Draft Lab", category=self.PracticalLab.Category.SOC,
            status=self.PracticalLab.Status.DRAFT,
        )
        summary = get_lab_summary(self.student)
        self.assertEqual(summary["total"], 0)


class CourseProgressServiceTests(TestCase):
    def setUp(self):
        from apps.enrollments.models import Enrollment, LessonProgress

        self.Enrollment = Enrollment
        self.LessonProgress = LessonProgress
        self.student = User.objects.create_user(
            email="courseprogress@example.com", password="pass1234", full_name="Course Progress",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )

    def test_module_progress_with_no_lessons_is_zero(self):
        course = _make_course(slug="cp-empty-module")
        module = CourseModule.objects.create(course=course, title="Empty Module", status="published")
        self.assertEqual(get_module_progress(self.student, module), 0)

    def test_module_progress_reflects_completed_fraction(self):
        course = _make_course(slug="cp-module")
        module = CourseModule.objects.create(course=course, title="M1", status="published")
        lessons = [
            Lesson.objects.create(module=module, title=f"L{i}", slug=f"cp-l{i}", status="published")
            for i in range(4)
        ]
        for lesson in lessons[:3]:
            self.LessonProgress.objects.create(student=self.student, lesson=lesson, completed=True)
        self.assertEqual(get_module_progress(self.student, module), 75)

    def test_course_module_breakdown_covers_all_published_modules(self):
        course = _make_course(slug="cp-breakdown")
        m1 = CourseModule.objects.create(course=course, title="M1", status="published", display_order=0)
        m2 = CourseModule.objects.create(course=course, title="M2", status="published", display_order=1)
        CourseModule.objects.create(course=course, title="Draft M", status="draft", display_order=2)
        Lesson.objects.create(module=m1, title="L1", slug="cp-b-l1", status="published")
        Lesson.objects.create(module=m2, title="L2", slug="cp-b-l2", status="published")

        breakdown = get_course_module_breakdown(self.student, course)
        self.assertEqual(len(breakdown), 2)  # draft module excluded
        self.assertEqual({row["module"].id for row in breakdown}, {m1.id, m2.id})

    def test_overall_academy_progress_weighted_across_courses(self):
        # Course A: 1 lesson, fully completed
        course_a = _make_course(slug="cp-a")
        module_a = CourseModule.objects.create(course=course_a, title="MA", status="published")
        lesson_a = Lesson.objects.create(module=module_a, title="LA", slug="cp-a-l1", status="published")
        self.LessonProgress.objects.create(student=self.student, lesson=lesson_a, completed=True)
        self.Enrollment.objects.create(student=self.student, course=course_a, status=self.Enrollment.Status.ACTIVE)

        # Course B: 9 lessons, none completed
        course_b = _make_course(slug="cp-b")
        module_b = CourseModule.objects.create(course=course_b, title="MB", status="published")
        for i in range(9):
            Lesson.objects.create(module=module_b, title=f"LB{i}", slug=f"cp-b-l{i}", status="published")
        self.Enrollment.objects.create(student=self.student, course=course_b, status=self.Enrollment.Status.ACTIVE)

        # A plain average of (100% + 0%) / 2 would be 50% — but weighted
        # by lesson count (1 of 10 total lessons completed), it's 10%.
        self.assertEqual(get_overall_academy_progress(self.student), 10)

    def test_overall_academy_progress_zero_with_no_enrollments(self):
        self.assertEqual(get_overall_academy_progress(self.student), 0)


class CohortStatsServiceTests(TestCase):
    def setUp(self):
        from apps.certificates.models import Certificate
        from apps.cohorts.models import Cohort, CohortMembership
        from apps.enrollments.models import Enrollment

        self.Certificate = Certificate
        self.Cohort = Cohort
        self.CohortMembership = CohortMembership
        self.Enrollment = Enrollment
        self.cohort = Cohort.objects.create(name="Test Cohort")

    def _add_member(self, email):
        student = User.objects.create_user(
            email=email, password="pass1234", full_name=email.split("@")[0],
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        self.CohortMembership.objects.create(cohort=self.cohort, student=student)
        return student

    def test_empty_cohort_returns_zeros_and_nones(self):
        stats = get_cohort_stats(self.cohort)
        self.assertEqual(stats["member_count"], 0)
        self.assertEqual(stats["total_enrollments"], 0)
        self.assertEqual(stats["completion_rate"], 0)
        self.assertEqual(stats["dropout_rate"], 0)
        self.assertIsNone(stats["average_score"])
        self.assertIsNone(stats["average_improvement"])
        self.assertEqual(stats["certificates_earned"], 0)

    def test_member_count_and_enrollment_totals(self):
        student1 = self._add_member("cohortmember1@example.com")
        student2 = self._add_member("cohortmember2@example.com")
        course = _make_course(slug="cohort-course")
        self.Enrollment.objects.create(student=student1, course=course, status=self.Enrollment.Status.ACTIVE)
        self.Enrollment.objects.create(student=student2, course=course, status=self.Enrollment.Status.COMPLETED)

        stats = get_cohort_stats(self.cohort)
        self.assertEqual(stats["member_count"], 2)
        self.assertEqual(stats["total_enrollments"], 2)
        self.assertEqual(stats["completion_rate"], 50.0)

    def test_dropout_rate_counts_withdrawn_and_suspended(self):
        student1 = self._add_member("dropout1@example.com")
        student2 = self._add_member("dropout2@example.com")
        student3 = self._add_member("dropout3@example.com")
        course = _make_course(slug="dropout-course")
        self.Enrollment.objects.create(student=student1, course=course, status=self.Enrollment.Status.WITHDRAWN)
        self.Enrollment.objects.create(student=student2, course=course, status=self.Enrollment.Status.SUSPENDED)
        self.Enrollment.objects.create(student=student3, course=course, status=self.Enrollment.Status.ACTIVE)

        stats = get_cohort_stats(self.cohort)
        self.assertAlmostEqual(stats["dropout_rate"], 66.7, places=1)

    def test_average_score_from_graded_quiz_attempts_only(self):
        student = self._add_member("scorestudent@example.com")
        course = _make_course(slug="score-course")
        quiz = Quiz.objects.create(course=course, title="Q1", status=Quiz.Status.PUBLISHED)
        QuizAttempt.objects.create(
            quiz=quiz, student=student, attempt_number=1, status=QuizAttempt.Status.GRADED,
            percentage=80.0, score=80, max_score=100, graded_at=timezone.now(),
        )
        QuizAttempt.objects.create(
            quiz=quiz, student=student, attempt_number=2, status=QuizAttempt.Status.GRADED,
            percentage=90.0, score=90, max_score=100, graded_at=timezone.now(),
        )
        QuizAttempt.objects.create(
            quiz=quiz, student=student, attempt_number=3, status=QuizAttempt.Status.IN_PROGRESS,
        )  # must be excluded — not graded

        stats = get_cohort_stats(self.cohort)
        self.assertEqual(stats["average_score"], 85.0)

    def test_average_improvement_reuses_skill_improvement_service(self):
        student = self._add_member("improvestudent@example.com")
        course = _make_course(slug="improve-course")
        self.Enrollment.objects.create(student=student, course=course, status=self.Enrollment.Status.ACTIVE)
        pre = Quiz.objects.create(course=course, title="Pre", status=Quiz.Status.PUBLISHED, quiz_type=Quiz.QuizType.PRE_TEST)
        post = Quiz.objects.create(course=course, title="Post", status=Quiz.Status.PUBLISHED, quiz_type=Quiz.QuizType.POST_TEST)
        QuizAttempt.objects.create(
            quiz=pre, student=student, attempt_number=1, status=QuizAttempt.Status.GRADED,
            percentage=30.0, score=30, max_score=100, graded_at=timezone.now(),
        )
        QuizAttempt.objects.create(
            quiz=post, student=student, attempt_number=1, status=QuizAttempt.Status.GRADED,
            percentage=80.0, score=80, max_score=100, graded_at=timezone.now(),
        )

        stats = get_cohort_stats(self.cohort)
        self.assertEqual(stats["average_improvement"], 50.0)

    def test_certificates_earned_only_counts_issued(self):
        student = self._add_member("certstudent@example.com")
        course = _make_course(slug="cert-course")
        self.Certificate.objects.create(student=student, course=course, status=self.Certificate.Status.ISSUED)
        other_course = _make_course(slug="cert-course-2")
        self.Certificate.objects.create(student=student, course=other_course, status=self.Certificate.Status.REVOKED)

        stats = get_cohort_stats(self.cohort)
        self.assertEqual(stats["certificates_earned"], 1)

    def test_non_members_never_counted(self):
        member = self._add_member("member@example.com")
        non_member = User.objects.create_user(
            email="nonmember@example.com", password="pass1234", full_name="Non Member",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        course = _make_course(slug="isolation-course")
        self.Enrollment.objects.create(student=member, course=course, status=self.Enrollment.Status.ACTIVE)
        self.Enrollment.objects.create(student=non_member, course=course, status=self.Enrollment.Status.ACTIVE)

        stats = get_cohort_stats(self.cohort)
        self.assertEqual(stats["total_enrollments"], 1)


class PlatformStatsServiceTests(TestCase):
    def setUp(self):
        from apps.certificates.models import Certificate
        from apps.enrollments.models import Enrollment
        from apps.feedback.models import StudentFeedback
        from apps.instructors.models import InstructorAssignment

        self.Certificate = Certificate
        self.Enrollment = Enrollment
        self.StudentFeedback = StudentFeedback
        self.InstructorAssignment = InstructorAssignment

    def _make_student(self, email):
        return User.objects.create_user(
            email=email, password="pass1234", full_name=email.split("@")[0],
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )

    def test_empty_platform_returns_zeros_and_nones(self):
        stats = get_platform_analytics()
        self.assertEqual(stats["total_enrollments"], 0)
        self.assertEqual(stats["completion_rate"], 0)
        self.assertEqual(stats["dropout_rate"], 0)
        self.assertEqual(stats["retention_rate"], 0)
        self.assertIsNone(stats["average_score"])
        self.assertIsNone(stats["avg_skill_improvement"])
        self.assertEqual(stats["certificates_issued"], 0)
        self.assertEqual(stats["top_courses"], [])
        self.assertEqual(stats["top_instructors"], [])

    def test_enrollment_completion_and_dropout_rates(self):
        student1 = self._make_student("plat1@example.com")
        student2 = self._make_student("plat2@example.com")
        student3 = self._make_student("plat3@example.com")
        course = _make_course(slug="platform-course")
        self.Enrollment.objects.create(student=student1, course=course, status=self.Enrollment.Status.COMPLETED)
        self.Enrollment.objects.create(student=student2, course=course, status=self.Enrollment.Status.WITHDRAWN)
        self.Enrollment.objects.create(student=student3, course=course, status=self.Enrollment.Status.ACTIVE)

        stats = get_platform_analytics()
        self.assertEqual(stats["total_enrollments"], 3)
        self.assertAlmostEqual(stats["completion_rate"], 33.3, places=1)
        self.assertAlmostEqual(stats["dropout_rate"], 33.3, places=1)
        self.assertAlmostEqual(stats["retention_rate"], 66.7, places=1)

    def test_certificates_issued_only_counts_issued_status(self):
        student = self._make_student("platcert@example.com")
        course = _make_course(slug="platform-cert-course")
        self.Certificate.objects.create(student=student, course=course, status=self.Certificate.Status.ISSUED)
        other_course = _make_course(slug="platform-cert-course-2")
        self.Certificate.objects.create(student=student, course=other_course, status=self.Certificate.Status.REVOKED)

        stats = get_platform_analytics()
        self.assertEqual(stats["certificates_issued"], 1)

    def test_top_courses_ranked_by_enrollment_count(self):
        popular = Course.objects.create(
            title="Popular Course", slug="popular-course", short_description="x", description="x",
            status=Course.Status.PUBLISHED,
        )
        quiet = Course.objects.create(
            title="Quiet Course", slug="quiet-course", short_description="x", description="x",
            status=Course.Status.PUBLISHED,
        )
        for i in range(3):
            student = self._make_student(f"popfan{i}@example.com")
            self.Enrollment.objects.create(student=student, course=popular, status=self.Enrollment.Status.ACTIVE)
        quiet_student = self._make_student("quietfan@example.com")
        self.Enrollment.objects.create(student=quiet_student, course=quiet, status=self.Enrollment.Status.ACTIVE)

        stats = get_platform_analytics()
        self.assertEqual(stats["top_courses"][0]["course__title"], popular.title)
        self.assertEqual(stats["top_courses"][0]["enrollment_count"], 3)

    def test_top_instructors_ranked_by_average_rating(self):
        course = _make_course(slug="rating-course")
        instructor = User.objects.create_user(
            email="platinstructor@example.com", password="pass1234", full_name="Top Instructor",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        self.InstructorAssignment.objects.create(instructor=instructor, course=course)
        student1 = self._make_student("ratingstudent1@example.com")
        student2 = self._make_student("ratingstudent2@example.com")
        self.Enrollment.objects.create(student=student1, course=course, status=self.Enrollment.Status.ACTIVE)
        self.Enrollment.objects.create(student=student2, course=course, status=self.Enrollment.Status.ACTIVE)
        self.StudentFeedback.objects.create(
            student=student1, course=course, instructor=instructor,
            overall_rating=5, content_quality=5, practical_lab_quality=5, platform_experience=5,
            difficulty=3, confidence_before=2, confidence_after=5, nps_score=9,
        )
        self.StudentFeedback.objects.create(
            student=student2, course=course, instructor=instructor,
            overall_rating=3, content_quality=3, practical_lab_quality=3, platform_experience=3,
            difficulty=3, confidence_before=2, confidence_after=4, nps_score=6,
        )

        stats = get_platform_analytics()
        self.assertEqual(stats["top_instructors"][0]["instructor__full_name"], "Top Instructor")
        self.assertEqual(stats["top_instructors"][0]["avg_rating"], 4.0)
        self.assertEqual(stats["top_instructors"][0]["response_count"], 2)
        self.assertEqual(stats["nps"]["total_responses"], 2)

    def test_skill_improvement_from_pre_and_post_test_averages(self):
        student = self._make_student("skillstudent@example.com")
        course = _make_course(slug="skill-course")
        pre = Quiz.objects.create(course=course, title="Pre", status=Quiz.Status.PUBLISHED, quiz_type=Quiz.QuizType.PRE_TEST)
        post = Quiz.objects.create(course=course, title="Post", status=Quiz.Status.PUBLISHED, quiz_type=Quiz.QuizType.POST_TEST)
        QuizAttempt.objects.create(
            quiz=pre, student=student, attempt_number=1, status=QuizAttempt.Status.GRADED,
            percentage=40.0, score=40, max_score=100, graded_at=timezone.now(),
        )
        QuizAttempt.objects.create(
            quiz=post, student=student, attempt_number=1, status=QuizAttempt.Status.GRADED,
            percentage=90.0, score=90, max_score=100, graded_at=timezone.now(),
        )

        stats = get_platform_analytics()
        self.assertEqual(stats["avg_pre_test"], 40.0)
        self.assertEqual(stats["avg_post_test"], 90.0)
        self.assertEqual(stats["avg_skill_improvement"], 50.0)

    def test_dau_mau_from_learning_sessions(self):
        student = self._make_student("sessionstudent@example.com")
        LearningSession.objects.create(user=student)
        old_session = LearningSession.objects.create(user=student)
        LearningSession.objects.filter(pk=old_session.pk).update(
            started_at=timezone.now() - datetime.timedelta(days=45)
        )

        stats = get_platform_analytics()
        self.assertEqual(stats["dau"], 1)
        self.assertEqual(stats["mau"], 1)


class ImpactDashboardServiceTests(TestCase):
    def setUp(self):
        from apps.enrollments.models import Enrollment
        from apps.labs.models import LabProgress, PracticalLab

        self.Enrollment = Enrollment
        self.LabProgress = LabProgress
        self.PracticalLab = PracticalLab

    def test_empty_platform_has_no_self_reported_snapshot(self):
        data = get_impact_dashboard_data()
        self.assertEqual(data["computed"]["people_trained"], 0)
        self.assertEqual(data["computed"]["labs_completed"], 0)
        self.assertIsNone(data["self_reported"]["smes_protected"])
        self.assertIsNone(data["self_reported"]["as_of"])

    def test_people_trained_counts_distinct_students_only(self):
        student = self._make_student("impactstudent@example.com")
        course1 = _make_course(slug="impact-course-1")
        course2 = _make_course(slug="impact-course-2")
        self.Enrollment.objects.create(student=student, course=course1, status=self.Enrollment.Status.ACTIVE)
        self.Enrollment.objects.create(student=student, course=course2, status=self.Enrollment.Status.ACTIVE)

        data = get_impact_dashboard_data()
        self.assertEqual(data["computed"]["people_trained"], 1)

    def test_labs_completed_counts_only_completed_status(self):
        student = self._make_student("labimpactstudent@example.com")
        course = _make_course(slug="impact-lab-course")
        lab1 = self.PracticalLab.objects.create(
            course=course, title="Lab 1", category=self.PracticalLab.Category.LINUX,
            status=self.PracticalLab.Status.PUBLISHED,
        )
        lab2 = self.PracticalLab.objects.create(
            course=course, title="Lab 2", category=self.PracticalLab.Category.NMAP,
            status=self.PracticalLab.Status.PUBLISHED,
        )
        self.LabProgress.objects.create(lab=lab1, student=student, status=self.LabProgress.Status.COMPLETED)
        self.LabProgress.objects.create(lab=lab2, student=student, status=self.LabProgress.Status.IN_PROGRESS)

        data = get_impact_dashboard_data()
        self.assertEqual(data["computed"]["labs_completed"], 1)

    def test_latest_snapshot_used_when_multiple_exist(self):
        from .models import ImpactSnapshot

        ImpactSnapshot.objects.create(smes_protected=10, healthcare_workers_trained=5, businesses_started=1)
        ImpactSnapshot.objects.create(smes_protected=20, healthcare_workers_trained=8, businesses_started=2)

        data = get_impact_dashboard_data()
        self.assertEqual(data["self_reported"]["smes_protected"], 20)
        self.assertEqual(data["self_reported"]["businesses_started"], 2)

    def _make_student(self, email):
        return User.objects.create_user(
            email=email, password="pass1234", full_name=email.split("@")[0],
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )


class AnalyticsAndImpactAPITests(TestCase):
    """16.M — the read-only REST API views over the same
    get_platform_analytics()/get_impact_dashboard_data() services the
    16.J/16.K dashboards already use, so these tests only need to prove
    the API wiring (auth, shape) works — the underlying math is already
    covered by PlatformStatsServiceTests/ImpactDashboardServiceTests."""

    def setUp(self):
        self.admin = User.objects.create_user(
            email="analyticsapiadmin@example.com", password="pass1234", full_name="Analytics API Admin",
            role=User.Role.ADMIN, status=User.Status.ACTIVE, is_staff=True,
        )
        self.student = User.objects.create_user(
            email="analyticsapistudent@example.com", password="pass1234", full_name="Analytics API Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )

    def test_admin_can_fetch_platform_analytics(self):
        self.client.login(username="analyticsapiadmin@example.com", password="pass1234")
        response = self.client.get(reverse("api-v1:api-analytics"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("dau", data)
        self.assertIn("employment", data)
        self.assertIn("nps", data)

    def test_admin_can_fetch_impact_dashboard(self):
        self.client.login(username="analyticsapiadmin@example.com", password="pass1234")
        response = self.client.get(reverse("api-v1:api-impact"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("computed", data)
        self.assertIn("self_reported", data)

    def test_student_cannot_access_analytics_api(self):
        self.client.login(username="analyticsapistudent@example.com", password="pass1234")
        response = self.client.get(reverse("api-v1:api-analytics"))
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_access_impact_api(self):
        self.client.login(username="analyticsapistudent@example.com", password="pass1234")
        response = self.client.get(reverse("api-v1:api-impact"))
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_access_either_api(self):
        response = self.client.get(reverse("api-v1:api-analytics"))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse("api-v1:api-impact"))
        self.assertEqual(response.status_code, 403)


class InstructorDashboardStatsServiceTests(TestCase):
    def setUp(self):
        from apps.instructors.models import InstructorAssignment

        self.instructor = User.objects.create_user(
            email="instrstats@example.com", password="pass1234", full_name="Instr Stats",
            role=User.Role.INSTRUCTOR, status=User.Status.ACTIVE,
        )
        self.course = _make_course(slug="instr-stats-course")
        InstructorAssignment.objects.create(
            instructor=self.instructor, course=self.course, status=InstructorAssignment.Status.ACTIVE,
        )

    def _make_student(self, email):
        return User.objects.create_user(
            email=email, password="pass1234", full_name=email.split("@")[0],
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )

    def test_empty_course_returns_zeros_and_nones(self):
        stats = get_instructor_dashboard_stats(self.instructor)
        self.assertEqual(stats["total_students"], 0)
        self.assertEqual(stats["active_this_week"], 0)
        self.assertIsNone(stats["average_quiz_score"])
        self.assertIsNone(stats["average_assignment_score"])
        self.assertEqual(stats["lab_completion_rate"], 0)
        self.assertEqual(stats["at_risk_students"], [])

    def test_only_scoped_to_this_instructors_assigned_courses(self):
        from apps.enrollments.models import Enrollment

        other_course = _make_course(slug="instr-stats-other-course")
        other_student = self._make_student("otherinstrstats@example.com")
        Enrollment.objects.create(student=other_student, course=other_course, status=Enrollment.Status.ACTIVE)

        stats = get_instructor_dashboard_stats(self.instructor)
        self.assertEqual(stats["total_students"], 0)

    def test_average_quiz_and_assignment_scores(self):
        from apps.assignments.models import Assignment, AssignmentSubmission
        from apps.enrollments.models import Enrollment

        student = self._make_student("instrstatsstudent@example.com")
        Enrollment.objects.create(student=student, course=self.course, status=Enrollment.Status.ACTIVE)
        quiz = Quiz.objects.create(course=self.course, title="Q1", status=Quiz.Status.PUBLISHED)
        QuizAttempt.objects.create(
            quiz=quiz, student=student, attempt_number=1, status=QuizAttempt.Status.GRADED,
            percentage=70.0, score=70, max_score=100, graded_at=timezone.now(),
        )
        assignment = Assignment.objects.create(course=self.course, title="A1", status=Assignment.Status.PUBLISHED)
        AssignmentSubmission.objects.create(
            assignment=assignment, student=student, status=AssignmentSubmission.Status.GRADED, score=80.0,
        )

        stats = get_instructor_dashboard_stats(self.instructor)
        self.assertEqual(stats["average_quiz_score"], 70.0)
        self.assertEqual(stats["average_assignment_score"], 80.0)

    def test_at_risk_flags_low_progress_and_excludes_healthy_students(self):
        from apps.enrollments.models import Enrollment

        at_risk_student = self._make_student("atriskstudent@example.com")
        healthy_student = self._make_student("healthystudent@example.com")
        Enrollment.objects.create(
            student=at_risk_student, course=self.course, status=Enrollment.Status.ACTIVE, progress_percentage=10,
        )
        Enrollment.objects.create(
            student=healthy_student, course=self.course, status=Enrollment.Status.ACTIVE, progress_percentage=90,
        )

        stats = get_instructor_dashboard_stats(self.instructor)
        names = [row["student_name"] for row in stats["at_risk_students"]]
        self.assertIn("atriskstudent", names)
        self.assertNotIn("healthystudent", names)

    def test_at_risk_flags_low_average_score_even_with_high_progress(self):
        from apps.enrollments.models import Enrollment

        struggling_student = self._make_student("strugglingstudent@example.com")
        Enrollment.objects.create(
            student=struggling_student, course=self.course, status=Enrollment.Status.ACTIVE,
            progress_percentage=90,
        )
        quiz = Quiz.objects.create(course=self.course, title="Hard Quiz", status=Quiz.Status.PUBLISHED)
        QuizAttempt.objects.create(
            quiz=quiz, student=struggling_student, attempt_number=1, status=QuizAttempt.Status.GRADED,
            percentage=20.0, score=20, max_score=100, graded_at=timezone.now(),
        )

        stats = get_instructor_dashboard_stats(self.instructor)
        names = [row["student_name"] for row in stats["at_risk_students"]]
        self.assertIn("strugglingstudent", names)

    def test_feedback_stats_reuse_nps_and_avg_rating(self):
        from apps.enrollments.models import Enrollment
        from apps.feedback.models import StudentFeedback

        student = self._make_student("instrfeedbackstudent@example.com")
        Enrollment.objects.create(student=student, course=self.course, status=Enrollment.Status.ACTIVE)
        StudentFeedback.objects.create(
            student=student, course=self.course, instructor=self.instructor,
            overall_rating=4, content_quality=4, practical_lab_quality=4, platform_experience=4,
            difficulty=3, confidence_before=2, confidence_after=4, nps_score=9,
        )

        stats = get_instructor_dashboard_stats(self.instructor)
        self.assertEqual(stats["feedback"]["average_rating"], 4.0)
        self.assertEqual(stats["feedback"]["response_count"], 1)
        self.assertEqual(stats["feedback"]["nps_score"], 100)


class FidImpactReportServiceTests(TestCase):
    def test_empty_platform_returns_expected_shape(self):
        data = get_fid_impact_report_data()
        self.assertIn("reach", data)
        self.assertIn("learning_outcomes", data)
        self.assertIn("employment_outcomes", data)
        self.assertIn("field_impact", data)
        self.assertEqual(data["cohorts"], [])
        self.assertEqual(data["top_courses"], [])
        self.assertIsNone(data["prepared_for"])

    def test_prepared_for_is_passed_through(self):
        data = get_fid_impact_report_data(prepared_for="Test Funder")
        self.assertEqual(data["prepared_for"], "Test Funder")

    def test_reuses_impact_stats_not_reimplemented(self):
        from apps.certificates.models import Certificate
        from apps.enrollments.models import Enrollment

        student = User.objects.create_user(
            email="fidstudent@example.com", password="pass1234", full_name="Fid Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        course = _make_course(slug="fid-course")
        Enrollment.objects.create(student=student, course=course, status=Enrollment.Status.COMPLETED)
        Certificate.objects.create(student=student, course=course, status=Certificate.Status.ISSUED)

        data = get_fid_impact_report_data()
        self.assertEqual(data["reach"]["people_trained"], 1)
        self.assertEqual(data["reach"]["certificates_issued"], 1)

    def test_cohort_breakdown_reflects_real_cohort(self):
        from apps.cohorts.models import Cohort, CohortMembership

        student = User.objects.create_user(
            email="fidcohortstudent@example.com", password="pass1234", full_name="Fid Cohort Student",
            role=User.Role.STUDENT, status=User.Status.ACTIVE,
        )
        cohort = Cohort.objects.create(name="FID Test Cohort")
        CohortMembership.objects.create(cohort=cohort, student=student)

        data = get_fid_impact_report_data()
        self.assertEqual(len(data["cohorts"]), 1)
        self.assertEqual(data["cohorts"][0]["name"], "FID Test Cohort")
        self.assertEqual(data["cohorts"][0]["member_count"], 1)
