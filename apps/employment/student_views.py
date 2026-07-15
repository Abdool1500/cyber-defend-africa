from django.contrib import messages
from django.shortcuts import render, redirect

from apps.accounts.permissions import student_required
from apps.core.services.storage import StorageError, generate_safe_path, get_storage_service

from .forms import EmploymentOutcomeForm
from .models import EmploymentOutcome


@student_required
def employment_list(request):
    outcomes = EmploymentOutcome.objects.filter(student=request.user)
    return render(request, "student/employment/list.html", {"outcomes": outcomes})


@student_required
def employment_create(request):
    if request.method == "POST":
        form = EmploymentOutcomeForm(request.POST, request.FILES)
        if form.is_valid():
            outcome = form.save(commit=False)
            outcome.student = request.user
            evidence = form.cleaned_data.get("evidence")
            if evidence:
                path = generate_safe_path(
                    "employment-evidence", str(request.user.id), original_filename=evidence.name,
                )
                try:
                    get_storage_service().upload(
                        "employment-evidence", path, evidence, content_type=evidence.content_type,
                    )
                except StorageError as exc:
                    messages.error(request, f"Evidence upload failed: {exc}")
                    return render(request, "student/employment/form.html", {"form": form})
                outcome.evidence_storage_path = path
            outcome.save()
            messages.success(request, "Employment update saved.")
            return redirect("student_employment:list")
    else:
        form = EmploymentOutcomeForm()
    return render(request, "student/employment/form.html", {"form": form})
