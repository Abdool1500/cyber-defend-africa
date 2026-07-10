import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.permissions import student_required
from apps.enrollments.models import Enrollment

from .models import AttemptQuestion, Quiz, QuizAttempt
from .services.attempts import (
    QuizAttemptError,
    get_in_progress_attempt,
    is_expired,
    save_answer,
    start_attempt,
    submit_attempt,
)


def _enrolled_course_ids(student):
    return list(
        Enrollment.objects.filter(student=student, status=Enrollment.Status.ACTIVE).values_list("course_id", flat=True)
    )


@student_required
def quiz_list(request):
    course_ids = _enrolled_course_ids(request.user)
    quizzes = Quiz.objects.filter(course_id__in=course_ids, status=Quiz.Status.PUBLISHED).select_related("course")
    return render(request, "student/quizzes/list.html", {"quizzes": quizzes})


@student_required
def quiz_detail(request, quiz_id):
    course_ids = _enrolled_course_ids(request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id, course_id__in=course_ids, status=Quiz.Status.PUBLISHED)
    attempts_used = QuizAttempt.objects.filter(quiz=quiz, student=request.user).count()
    in_progress = get_in_progress_attempt(quiz, request.user)
    return render(request, "student/quizzes/detail.html", {
        "quiz": quiz, "attempts_used": attempts_used, "in_progress": in_progress,
    })


@student_required
def quiz_start(request, quiz_id):
    course_ids = _enrolled_course_ids(request.user)
    quiz = get_object_or_404(Quiz, id=quiz_id, course_id__in=course_ids, status=Quiz.Status.PUBLISHED)

    existing = get_in_progress_attempt(quiz, request.user)
    if existing:
        return redirect("student_quizzes:attempt", attempt_id=existing.id)

    try:
        attempt = start_attempt(quiz, request.user)
    except QuizAttemptError as exc:
        messages.error(request, str(exc))
        return redirect("student_quizzes:detail", quiz_id=quiz.id)

    return redirect("student_quizzes:attempt", attempt_id=attempt.id)


@student_required
def attempt_list(request):
    attempts = QuizAttempt.objects.filter(student=request.user).select_related("quiz", "quiz__course").order_by("-started_at")
    return render(request, "student/attempts/list.html", {"attempts": attempts})


@student_required
def attempt_detail(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)

    if attempt.status == QuizAttempt.Status.IN_PROGRESS:
        if is_expired(attempt):
            submit_attempt(attempt)
            return redirect("student_quizzes:results", attempt_id=attempt.id)
        attempt_questions = attempt.attempt_questions.select_related("question").prefetch_related(
            "question__options", "answer", "answer__selected_options"
        ).order_by("display_order")
        return render(request, "student/attempts/take.html", {
            "attempt": attempt, "attempt_questions": _build_take_payload(attempt_questions),
        })

    return redirect("student_quizzes:results", attempt_id=attempt.id)


def _build_take_payload(attempt_questions):
    """Builds a student-safe view of each attempt question — option text
    and frozen display order only, never is_correct/model_answer/
    grading_guidance. Options are ordered per the frozen
    option_order_snapshot so a shuffle doesn't reshuffle on refresh."""
    payload = []
    for aq in attempt_questions:
        # option_order_snapshot stores ids as strings (JSONField can't
        # serialize UUID objects), so key the lookup dict by string too.
        options_by_id = {str(o.id): o for o in aq.question.options.all()}
        ordered_ids = aq.option_order_snapshot or list(options_by_id.keys())
        ordered_options = [options_by_id[oid] for oid in ordered_ids if oid in options_by_id]

        existing_answer = getattr(aq, "answer", None)
        selected_ids = set()
        text_answer = ""
        if existing_answer:
            # Real UUID objects here (not the string snapshot ids) — this
            # matches option.id's type in the template's `in` check below.
            selected_ids = {o.id for o in existing_answer.selected_options.all()}
            text_answer = existing_answer.text_answer

        payload.append({
            "attempt_question": aq,
            "options": ordered_options,
            "selected_ids": selected_ids,
            "text_answer": text_answer,
        })
    return payload


@student_required
def attempt_results(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz", "quiz__course"), id=attempt_id, student=request.user
    )
    quiz = attempt.quiz
    show_answers = quiz.show_correct_answers and attempt.status == QuizAttempt.Status.GRADED
    answers = None
    if show_answers:
        answers = attempt.answers.select_related("attempt_question__question").prefetch_related(
            "attempt_question__question__options"
        ).order_by("attempt_question__display_order")
    return render(request, "student/attempts/results.html", {
        "attempt": attempt, "quiz": quiz, "show_answers": show_answers, "answers": answers,
    })


@student_required
@require_POST
def save_answer_api(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid payload."}, status=400)

    attempt_question = get_object_or_404(
        AttemptQuestion, id=payload.get("attempt_question_id"), attempt=attempt
    )
    try:
        save_answer(
            attempt,
            attempt_question,
            option_ids=payload.get("option_ids"),
            text_answer=payload.get("text_answer"),
        )
    except QuizAttemptError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse({"status": "saved"})


@student_required
@require_POST
def submit_attempt_api(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    try:
        submit_attempt(attempt)
    except QuizAttemptError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse({"status": "submitted", "redirect_url": f"/student/attempts/{attempt.id}/results/"})
