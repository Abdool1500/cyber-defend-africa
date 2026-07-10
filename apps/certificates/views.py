from django.shortcuts import render

from apps.accounts.permissions import student_required

from .models import Certificate


def verify_certificate(request, code):
    certificate = Certificate.objects.filter(verification_code=code).select_related("student", "course").first()
    return render(request, "public/certificate_verify.html", {"certificate": certificate})


@student_required
def student_certificate_list(request):
    certificates = Certificate.objects.filter(student=request.user, status=Certificate.Status.ISSUED).select_related("course")
    return render(request, "student/certificates/list.html", {"certificates": certificates})
