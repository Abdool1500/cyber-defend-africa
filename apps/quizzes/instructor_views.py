from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.permissions import instructor_required
from apps.instructors.models import InstructorAssignment
from apps.question_bank.models import Question

from .forms import QuizForm, QuizRandomRuleForm
from .models import Quiz, QuizAttempt, QuizQuestion, QuizRandomRule
from .services.grading import finalize_manual_grade


def _assigned_course_ids(instructor):
    return list(
        InstructorAssignment.objects.filter(
            instructor=instructor, status=InstructorAssignment.Status.ACTIVE
        ).values_list("course_id", flat=True)
    )


def _get_owned_quiz(instructor, quiz_id):
    return get_object_or_404(Quiz, id=quiz_id, course_id__in=_assigned_course_ids(instructor))


@instructor_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(course_id__in=_assigned_course_ids(request.user)).select_related("course")
    return render(request, "instructor/quizzes/list.html", {"quizzes": quizzes})


@instructor_required
def quiz_create(request):
    if request.method == "POST":
        form = QuizForm(request.POST, instructor=request.user)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.status = Quiz.Status.DRAFT
            quiz.save()
            messages.success(request, "Quiz created. Add questions before publishing.")
            return redirect("instructor_quizzes:edit", quiz_id=quiz.id)
    else:
        form = QuizForm(instructor=request.user)
    return render(request, "instructor/quizzes/form.html", {"form": form, "is_edit": False})


@instructor_required
def quiz_edit(request, quiz_id):
    quiz = _get_owned_quiz(request.user, quiz_id)
    if request.method == "POST":
        form = QuizForm(request.POST, instance=quiz, instructor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Quiz updated.")
            return redirect("instructor_quizzes:edit", quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz, instructor=request.user)

    quiz_questions = quiz.quiz_questions.select_related("question").order_by("display_order")
    added_ids = quiz_questions.values_list("question_id", flat=True)
    available_questions = Question.objects.filter(
        course=quiz.course, status=Question.Status.PUBLISHED
    ).exclude(id__in=added_ids)
    random_rules = quiz.random_rules.all()
    random_rule_form = QuizRandomRuleForm()

    return render(request, "instructor/quizzes/form.html", {
        "form": form, "is_edit": True, "quiz": quiz,
        "quiz_questions": quiz_questions,
        "available_questions": available_questions,
        "random_rules": random_rules,
        "random_rule_form": random_rule_form,
    })


@instructor_required
def quiz_add_question(request, quiz_id):
    quiz = _get_owned_quiz(request.user, quiz_id)
    question = get_object_or_404(Question, id=request.POST.get("question_id"), course=quiz.course)
    next_order = (quiz.quiz_questions.count() or 0) + 1
    QuizQuestion.objects.get_or_create(quiz=quiz, question=question, defaults={"display_order": next_order})
    messages.success(request, "Question added to quiz.")
    return redirect("instructor_quizzes:edit", quiz_id=quiz.id)


@instructor_required
def quiz_remove_question(request, quiz_id, quiz_question_id):
    quiz = _get_owned_quiz(request.user, quiz_id)
    QuizQuestion.objects.filter(id=quiz_question_id, quiz=quiz).delete()
    messages.success(request, "Question removed from quiz.")
    return redirect("instructor_quizzes:edit", quiz_id=quiz.id)


@instructor_required
def quiz_add_random_rule(request, quiz_id):
    quiz = _get_owned_quiz(request.user, quiz_id)
    form = QuizRandomRuleForm(request.POST)
    if form.is_valid():
        rule = form.save(commit=False)
        rule.quiz = quiz
        rule.save()
        available = rule.matching_questions().count()
        if available < rule.number_of_questions:
            messages.warning(
                request,
                f"Warning: only {available} published question(s) match this rule, but "
                f"{rule.number_of_questions} are required. Add more questions before publishing.",
            )
        else:
            messages.success(request, "Random rule added.")
    else:
        messages.error(request, "Could not add random rule — check the values provided.")
    return redirect("instructor_quizzes:edit", quiz_id=quiz.id)


@instructor_required
def quiz_remove_random_rule(request, quiz_id, rule_id):
    quiz = _get_owned_quiz(request.user, quiz_id)
    QuizRandomRule.objects.filter(id=rule_id, quiz=quiz).delete()
    messages.success(request, "Random rule removed.")
    return redirect("instructor_quizzes:edit", quiz_id=quiz.id)


@instructor_required
def quiz_publish(request, quiz_id):
    quiz = _get_owned_quiz(request.user, quiz_id)
    has_questions = quiz.quiz_questions.exists() or quiz.random_rules.exists()
    if not has_questions:
        messages.error(request, "Add at least one question or random rule before publishing.")
        return redirect("instructor_quizzes:edit", quiz_id=quiz.id)

    for rule in quiz.random_rules.all():
        available = rule.matching_questions().count()
        if available < rule.number_of_questions:
            messages.error(
                request,
                f"Cannot publish — a random rule requires {rule.number_of_questions} question(s) "
                f"but only {available} are available.",
            )
            return redirect("instructor_quizzes:edit", quiz_id=quiz.id)

    quiz.status = Quiz.Status.PUBLISHED
    quiz.save(update_fields=["status", "updated_at"])
    messages.success(request, "Quiz published.")
    return redirect("instructor_quizzes:edit", quiz_id=quiz.id)


@instructor_required
def quiz_unpublish(request, quiz_id):
    quiz = _get_owned_quiz(request.user, quiz_id)
    quiz.status = Quiz.Status.DRAFT
    quiz.save(update_fields=["status", "updated_at"])
    messages.success(request, "Quiz moved back to draft.")
    return redirect("instructor_quizzes:edit", quiz_id=quiz.id)


# --- Grading -------------------------------------------------------------

@instructor_required
def grading_list(request):
    course_ids = _assigned_course_ids(request.user)
    attempts = QuizAttempt.objects.filter(
        quiz__course_id__in=course_ids,
        status__in=[QuizAttempt.Status.PENDING_MANUAL_GRADING, QuizAttempt.Status.GRADED],
    ).select_related("quiz", "student", "quiz__course").order_by("-submitted_at")
    return render(request, "instructor/grading/list.html", {"attempts": attempts})


@instructor_required
def grading_detail(request, attempt_id):
    course_ids = _assigned_course_ids(request.user)
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz", "student", "quiz__course"),
        id=attempt_id, quiz__course_id__in=course_ids,
    )
    answers = attempt.answers.select_related("attempt_question__question").order_by("attempt_question__display_order")

    if request.method == "POST":
        for answer in answers:
            if answer.attempt_question.question.question_type != "short_answer":
                continue
            points_key = f"points_{answer.id}"
            feedback_key = f"feedback_{answer.id}"
            if points_key in request.POST:
                raw_points = request.POST.get(points_key, "").strip()
                max_points = answer.attempt_question.points
                try:
                    points = float(raw_points) if raw_points else 0
                except ValueError:
                    messages.error(request, "Points must be a number.")
                    continue
                # Server-side clamp: score can never exceed the question's max points.
                points = max(0, min(points, max_points))
                answer.awarded_points = points
                answer.instructor_feedback = request.POST.get(feedback_key, "")
                answer.graded_by = request.user
                from django.utils import timezone
                answer.graded_at = timezone.now()
                answer.save()

        if "finalize" in request.POST:
            try:
                finalize_manual_grade(attempt, request.user)
                messages.success(request, "Attempt finalized and score updated.")
            except ValueError as exc:
                messages.error(request, str(exc))
        else:
            messages.success(request, "Grades saved.")
        return redirect("instructor_grading:detail", attempt_id=attempt.id)

    return render(request, "instructor/grading/detail.html", {"attempt": attempt, "answers": answers})
