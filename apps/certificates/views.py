import io

import qrcode
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from apps.accounts.permissions import student_required
from apps.instructors.models import InstructorAssignment

from .models import Certificate


def _instructor_names(course):
    names = InstructorAssignment.objects.filter(
        course=course, status=InstructorAssignment.Status.ACTIVE,
    ).select_related("instructor").values_list("instructor__full_name", flat=True)
    return ", ".join(names) if names else None


def verify_certificate(request, code):
    certificate = Certificate.objects.filter(verification_code=code).select_related("student", "course").first()
    context = {"certificate": certificate}
    if certificate:
        context["instructor_names"] = _instructor_names(certificate.course)
        context["verification_url"] = request.build_absolute_uri(
            reverse("certificates:verify", args=[certificate.verification_code])
        )
    return render(request, "public/certificate_verify.html", context)


def certificate_qr_code(request, code):
    """On-the-fly QR code encoding the public verification URL — no
    Supabase Storage dependency, always reflects the current status
    (e.g. if a certificate is later revoked, the QR still resolves to a
    verification page that says so)."""
    if not Certificate.objects.filter(verification_code=code).exists():
        raise Http404("No certificate found for this code.")
    verify_url = request.build_absolute_uri(reverse("certificates:verify", args=[code]))
    img = qrcode.make(verify_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")


@student_required
def student_certificate_list(request):
    certificates = Certificate.objects.filter(student=request.user, status=Certificate.Status.ISSUED).select_related("course")
    return render(request, "student/certificates/list.html", {"certificates": certificates})
