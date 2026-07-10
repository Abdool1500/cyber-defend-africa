"""Secure quiz attempt lifecycle: starting an attempt freezes the exact
question set and order server-side inside a transaction, so a page refresh
can never re-randomize a student's quiz or hand them a new question set.
"""
import random

from django.db import transaction
from django.utils import timezone

from apps.enrollments.models import Enrollment
from apps.quizzes.models import AttemptQuestion, Quiz, QuizAttempt, QuizQuestion


class QuizAttemptError(Exception):
    """Raised for any condition that should block starting/resuming an
    attempt (not enrolled, not published, outside window, limit reached)."""


def _assert_can_start(quiz: Quiz, student):
    if quiz.status != Quiz.Status.PUBLISHED:
        raise QuizAttemptError("This quiz is not currently available.")

    is_enrolled = Enrollment.objects.filter(
        student=student, course=quiz.course, status=Enrollment.Status.ACTIVE
    ).exists()
    if not is_enrolled:
        raise QuizAttemptError("You must be enrolled in this course to take this quiz.")

    now = timezone.now()
    if quiz.available_from and now < quiz.available_from:
        raise QuizAttemptError("This quiz is not yet available.")
    if quiz.available_until and now > quiz.available_until:
        raise QuizAttemptError("This quiz is no longer available.")

    existing_attempts = QuizAttempt.objects.filter(quiz=quiz, student=student).count()
    if existing_attempts >= quiz.attempt_limit:
        raise QuizAttemptError("You have reached the maximum number of attempts for this quiz.")

    return existing_attempts


def get_in_progress_attempt(quiz: Quiz, student):
    return QuizAttempt.objects.filter(
        quiz=quiz, student=student, status=QuizAttempt.Status.IN_PROGRESS
    ).first()


@transaction.atomic
def start_attempt(quiz: Quiz, student) -> QuizAttempt:
    """Creates a new QuizAttempt with a frozen, secure question set.
    Re-entering an already in-progress attempt should use
    get_in_progress_attempt instead of calling this again."""
    existing_attempts = _assert_can_start(quiz, student)

    quiz_questions = list(
        QuizQuestion.objects.filter(quiz=quiz).select_related("question").order_by("display_order")
    )
    manual_question_ids = {qq.question_id for qq in quiz_questions}

    random_pool = []
    for rule in quiz.random_rules.all():
        candidates = list(rule.matching_questions().exclude(id__in=manual_question_ids))
        random.shuffle(candidates)
        chosen = candidates[: rule.number_of_questions]
        if len(chosen) < rule.number_of_questions:
            raise QuizAttemptError(
                "This quiz cannot be started right now — not enough published questions "
                "are available to satisfy its random selection rules."
            )
        random_pool.extend(chosen)
        manual_question_ids.update(q.id for q in chosen)

    selected = [(qq.question, qq.points()) for qq in quiz_questions] + [
        (q, q.default_points) for q in random_pool
    ]

    if not selected:
        raise QuizAttemptError("This quiz has no questions configured yet.")

    if quiz.shuffle_questions:
        random.shuffle(selected)

    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        student=student,
        attempt_number=existing_attempts + 1,
        expires_at=(
            timezone.now() + timezone.timedelta(minutes=quiz.time_limit_minutes)
            if quiz.time_limit_minutes
            else None
        ),
    )

    for order, (question, points) in enumerate(selected, start=1):
        # JSONField can't serialize UUID objects directly, so the frozen
        # snapshot stores option ids as strings.
        option_ids = [str(oid) for oid in question.options.values_list("id", flat=True)]
        if quiz.shuffle_options:
            random.shuffle(option_ids)
        AttemptQuestion.objects.create(
            attempt=attempt,
            question=question,
            display_order=order,
            points=points,
            option_order_snapshot=option_ids,
        )
        question.mark_locked_if_used()

    return attempt


def is_expired(attempt: QuizAttempt) -> bool:
    if not attempt.expires_at:
        return False
    return timezone.now() > attempt.expires_at


@transaction.atomic
def save_answer(attempt: QuizAttempt, attempt_question, *, option_ids=None, text_answer=None):
    """Autosave a single answer. Never grades here — grading only happens
    at submission time, server-side."""
    from apps.quizzes.models import QuizAnswer

    if attempt.status != QuizAttempt.Status.IN_PROGRESS:
        raise QuizAttemptError("This attempt is no longer in progress.")
    if is_expired(attempt):
        raise QuizAttemptError("This attempt has expired.")

    answer, _ = QuizAnswer.objects.get_or_create(
        attempt=attempt, attempt_question=attempt_question, student=attempt.student
    )
    if option_ids is not None:
        # option_ids arrives from the frontend as strings (JSON payload);
        # compare as strings so a valid UUID sent as text isn't silently
        # dropped here and never actually saved as a selection.
        valid_ids = {str(oid) for oid in attempt_question.question.options.values_list("id", flat=True)}
        answer.selected_options.set([oid for oid in option_ids if str(oid) in valid_ids])
    if text_answer is not None:
        answer.text_answer = text_answer
        answer.save(update_fields=["text_answer", "updated_at"])
    return answer


@transaction.atomic
def submit_attempt(attempt: QuizAttempt) -> QuizAttempt:
    """Finalizes an attempt. Expired attempts are still allowed to submit
    (auto-submission on timeout) — they're graded on whatever answers were
    saved before expiry, since save_answer already refuses to accept new
    answers once expired. Only an already-submitted attempt is rejected,
    which prevents duplicate submission."""
    from apps.quizzes.services.grading import grade_attempt

    if attempt.status != QuizAttempt.Status.IN_PROGRESS:
        raise QuizAttemptError("This attempt has already been submitted.")

    attempt.submitted_at = timezone.now()
    attempt.status = QuizAttempt.Status.SUBMITTED
    attempt.save(update_fields=["submitted_at", "status"])

    return grade_attempt(attempt)
