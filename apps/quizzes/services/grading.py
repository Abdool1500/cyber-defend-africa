"""Server-side quiz grading. This is the single place that decides what a
student's answer is worth — nothing submitted by the browser (score,
percentage, is_correct, awarded_points) is ever trusted directly.
"""
from django.db import transaction
from django.utils import timezone

from apps.question_bank.models import Question
from apps.quizzes.models import QuizAttempt


def grade_answer(answer):
    """Grades a single QuizAnswer in place based on its question type.
    Short answer questions are never auto-graded — they're left for an
    instructor and flip the attempt into pending_manual_grading."""
    question = answer.attempt_question.question
    max_points = answer.attempt_question.points

    if question.question_type in (Question.QuestionType.MULTIPLE_CHOICE, Question.QuestionType.TRUE_FALSE):
        selected_ids = set(answer.selected_options.values_list("id", flat=True))
        correct_ids = set(question.options.filter(is_correct=True).values_list("id", flat=True))
        answer.is_correct = selected_ids == correct_ids and len(selected_ids) > 0
        answer.awarded_points = max_points if answer.is_correct else 0

    elif question.question_type == Question.QuestionType.MULTIPLE_SELECT:
        selected_ids = set(answer.selected_options.values_list("id", flat=True))
        correct_ids = set(question.options.filter(is_correct=True).values_list("id", flat=True))
        # Exact-match default (spec 54): the selected set must equal the
        # correct set exactly — partial credit is not awarded by default.
        answer.is_correct = selected_ids == correct_ids
        answer.awarded_points = max_points if answer.is_correct else 0

    elif question.question_type == Question.QuestionType.SHORT_ANSWER:
        answer.is_correct = None
        answer.awarded_points = None

    answer.save(update_fields=["is_correct", "awarded_points", "updated_at"])
    return answer


@transaction.atomic
def grade_attempt(attempt: QuizAttempt):
    """Auto-grades every objective answer, then recalculates the attempt's
    aggregate score server-side. If any short-answer question is still
    ungraded, the attempt is marked pending_manual_grading instead of
    graded — a human must finalize it."""
    answers = attempt.answers.select_related("attempt_question__question").select_for_update()
    for answer in answers:
        if answer.attempt_question.question.question_type != Question.QuestionType.SHORT_ANSWER:
            grade_answer(answer)

    answers = attempt.answers.select_related("attempt_question")
    max_score = sum(aq.points for aq in attempt.attempt_questions.all())
    ungraded_short_answers = answers.filter(awarded_points__isnull=True).exists()

    if ungraded_short_answers:
        attempt.status = QuizAttempt.Status.PENDING_MANUAL_GRADING
        attempt.requires_manual_grading = True
        attempt.max_score = max_score
        attempt.save(update_fields=["status", "requires_manual_grading", "max_score"])
        return attempt

    score = sum(a.awarded_points or 0 for a in answers)
    attempt.score = score
    attempt.max_score = max_score
    attempt.percentage = round((score / max_score) * 100, 2) if max_score else 0
    attempt.status = QuizAttempt.Status.GRADED
    attempt.requires_manual_grading = False
    attempt.graded_at = timezone.now()
    attempt.save(update_fields=[
        "score", "max_score", "percentage", "status", "requires_manual_grading", "graded_at",
    ])
    return attempt


@transaction.atomic
def finalize_manual_grade(attempt: QuizAttempt, grader):
    """Called by an instructor after manually grading all short-answer
    questions on a pending attempt. Recomputes the final score server-side
    from whatever awarded_points the instructor has saved."""
    answers = attempt.answers.select_related("attempt_question")
    if answers.filter(awarded_points__isnull=True).exists():
        raise ValueError("All questions must be graded before finalizing this attempt.")

    max_score = sum(aq.points for aq in attempt.attempt_questions.all())
    score = sum(a.awarded_points or 0 for a in answers)
    attempt.score = score
    attempt.max_score = max_score
    attempt.percentage = round((score / max_score) * 100, 2) if max_score else 0
    attempt.status = QuizAttempt.Status.GRADED
    attempt.requires_manual_grading = False
    attempt.graded_at = timezone.now()
    attempt.graded_by = grader
    attempt.save(update_fields=[
        "score", "max_score", "percentage", "status", "requires_manual_grading",
        "graded_at", "graded_by",
    ])
    return attempt
