"""Pre-test / post-test skill improvement calculation.

Server-side only, like every other score calculation in this platform
(see apps/quizzes/services/grading.py) — a student's improvement is
derived from their graded QuizAttempt.percentage values, never trusted
from the client.
"""
from apps.quizzes.models import Quiz, QuizAttempt


def _latest_graded_percentage(quiz, student):
    if quiz is None:
        return None
    attempt = (
        QuizAttempt.objects.filter(quiz=quiz, student=student, status=QuizAttempt.Status.GRADED)
        .order_by("-started_at")
        .first()
    )
    return attempt


def get_skill_improvement(student, course):
    """Returns a dict describing a student's pre-test -> post-test
    improvement for one course. Every value is None/False until the
    relevant quiz exists and has been graded — callers must handle the
    "not available yet" state explicitly rather than assuming zeros."""
    result = {
        "pre_test_quiz": Quiz.objects.filter(course=course, quiz_type=Quiz.QuizType.PRE_TEST).first(),
        "post_test_quiz": Quiz.objects.filter(course=course, quiz_type=Quiz.QuizType.POST_TEST).first(),
        "pre_test_percentage": None,
        "post_test_percentage": None,
        "improvement": None,
        "normalized_gain": None,
        "passed_post_test": None,
        "complete": False,
    }

    pre_attempt = _latest_graded_percentage(result["pre_test_quiz"], student)
    if pre_attempt is not None:
        result["pre_test_percentage"] = pre_attempt.percentage

    post_attempt = _latest_graded_percentage(result["post_test_quiz"], student)
    if post_attempt is not None:
        result["post_test_percentage"] = post_attempt.percentage
        result["passed_post_test"] = post_attempt.passed

    pre = result["pre_test_percentage"]
    post = result["post_test_percentage"]
    if pre is not None and post is not None:
        result["improvement"] = round(post - pre, 2)
        # Normalized (Hake) gain: how much of the *possible* improvement
        # was captured — e.g. going from 90% to 95% is a much bigger
        # relative achievement than the same 5 points from 35% to 40%.
        result["normalized_gain"] = round((post - pre) / (100 - pre) * 100, 2) if pre < 100 else 0.0
        result["complete"] = True

    return result
