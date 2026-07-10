from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.permissions import instructor_required
from apps.instructors.models import InstructorAssignment

from .forms import QuestionForm, QuestionOptionFormSet, validate_options_for_type
from .models import Question, QuestionOption


def _assigned_course_ids(instructor):
    return list(
        InstructorAssignment.objects.filter(
            instructor=instructor, status=InstructorAssignment.Status.ACTIVE
        ).values_list("course_id", flat=True)
    )


def _get_owned_question(instructor, question_id):
    """Fetches a question scoped to courses the instructor is assigned to
    — this is the server-side guard against editing another instructor's
    question bank, not just hiding a link in the UI."""
    return get_object_or_404(
        Question, id=question_id, course_id__in=_assigned_course_ids(instructor)
    )


@instructor_required
def question_list(request):
    course_ids = _assigned_course_ids(request.user)
    questions = Question.objects.filter(course_id__in=course_ids).select_related("course", "module")

    search = request.GET.get("q", "").strip()
    if search:
        from django.db.models import Q

        questions = questions.filter(Q(question_text__icontains=search) | Q(topic__icontains=search))

    course_filter = request.GET.get("course")
    if course_filter:
        questions = questions.filter(course_id=course_filter)
    module_filter = request.GET.get("module")
    if module_filter:
        questions = questions.filter(module_id=module_filter)
    topic_filter = request.GET.get("topic")
    if topic_filter:
        questions = questions.filter(topic=topic_filter)
    type_filter = request.GET.get("type")
    if type_filter:
        questions = questions.filter(question_type=type_filter)
    difficulty_filter = request.GET.get("difficulty")
    if difficulty_filter:
        questions = questions.filter(difficulty=difficulty_filter)
    status_filter = request.GET.get("status")
    if status_filter:
        questions = questions.filter(status=status_filter)
    else:
        questions = questions.exclude(status=Question.Status.ARCHIVED)

    summary = {
        "total": Question.objects.filter(course_id__in=course_ids).count(),
        "published": Question.objects.filter(course_id__in=course_ids, status=Question.Status.PUBLISHED).count(),
        "draft": Question.objects.filter(course_id__in=course_ids, status=Question.Status.DRAFT).count(),
        "archived": Question.objects.filter(course_id__in=course_ids, status=Question.Status.ARCHIVED).count(),
    }

    paginator = Paginator(questions, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "instructor/question_bank/list.html", {
        "page_obj": page_obj,
        "summary": summary,
        "question_types": Question.QuestionType.choices,
        "difficulties": Question.Difficulty.choices,
        "statuses": Question.Status.choices,
        "assigned_courses": InstructorAssignment.objects.filter(
            instructor=request.user, status=InstructorAssignment.Status.ACTIVE
        ).select_related("course"),
    })


@instructor_required
def question_create(request):
    if request.method == "POST":
        form = QuestionForm(request.POST, instructor=request.user)
        formset = QuestionOptionFormSet(request.POST, instance=Question())
        needs_options = request.POST.get("question_type") != Question.QuestionType.SHORT_ANSWER
        if form.is_valid() and (not needs_options or formset.is_valid()):
            try:
                if needs_options:
                    validate_options_for_type(form.cleaned_data["question_type"], formset)
                question = form.save(commit=False)
                question.created_by = request.user
                question.save()
                if needs_options:
                    formset.instance = question
                    formset.save()
                messages.success(request, "Question created.")
                return redirect("instructor_question_bank:list")
            except Exception as exc:
                form.add_error(None, str(exc))
    else:
        form = QuestionForm(instructor=request.user)
        formset = QuestionOptionFormSet(instance=Question())
    return render(request, "instructor/question_bank/form.html", {"form": form, "formset": formset, "is_edit": False})


@instructor_required
def question_edit(request, question_id):
    question = _get_owned_question(request.user, question_id)
    if question.is_locked:
        messages.warning(
            request,
            "This question has already been used in a submitted quiz attempt and can no longer be "
            "edited in place — duplicate it instead to make changes.",
        )
        return redirect("instructor_question_bank:preview", question_id=question.id)

    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question, instructor=request.user)
        formset = QuestionOptionFormSet(request.POST, instance=question)
        needs_options = request.POST.get("question_type") != Question.QuestionType.SHORT_ANSWER
        if form.is_valid() and (not needs_options or formset.is_valid()):
            try:
                if needs_options:
                    validate_options_for_type(form.cleaned_data["question_type"], formset)
                form.save()
                if needs_options:
                    formset.save()
                messages.success(request, "Question updated.")
                return redirect("instructor_question_bank:list")
            except Exception as exc:
                form.add_error(None, str(exc))
    else:
        form = QuestionForm(instance=question, instructor=request.user)
        formset = QuestionOptionFormSet(instance=question)
    return render(request, "instructor/question_bank/form.html", {"form": form, "formset": formset, "is_edit": True, "question": question})


@instructor_required
def question_preview(request, question_id):
    question = _get_owned_question(request.user, question_id)
    return render(request, "instructor/question_bank/preview.html", {"question": question})


@instructor_required
def question_duplicate(request, question_id):
    question = _get_owned_question(request.user, question_id)
    options = list(question.options.all())
    question.pk = None
    question.id = None
    question.status = Question.Status.DRAFT
    question.is_locked = False
    question.created_by = request.user
    question.save()
    for option in options:
        QuestionOption.objects.create(
            question=question,
            option_text=option.option_text,
            is_correct=option.is_correct,
            display_order=option.display_order,
        )
    messages.success(request, "Question duplicated as a new draft.")
    return redirect("instructor_question_bank:edit", question_id=question.id)


@instructor_required
def question_archive(request, question_id):
    question = _get_owned_question(request.user, question_id)
    question.status = Question.Status.ARCHIVED
    question.is_archived = True
    question.save(update_fields=["status", "is_archived", "updated_at"])
    messages.success(request, "Question archived.")
    return redirect("instructor_question_bank:list")


@instructor_required
def question_restore(request, question_id):
    question = _get_owned_question(request.user, question_id)
    question.status = Question.Status.DRAFT
    question.is_archived = False
    question.save(update_fields=["status", "is_archived", "updated_at"])
    messages.success(request, "Question restored to draft.")
    return redirect("instructor_question_bank:list")
