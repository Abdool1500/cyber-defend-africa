from django.views.generic import TemplateView


class AcademyHomeView(TemplateView):
    template_name = "public/academy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["benefits"] = [
            "Hands-On Learning",
            "Practical Labs",
            "Real-World Projects",
            "Structured Learning Paths",
            "Assessments",
            "Quizzes",
            "Instructor Support",
            "Student Dashboard",
            "Certificates",
            "Career Development",
            "Progress Tracking",
        ]
        return context


class CareerPathAssessmentView(TemplateView):
    template_name = "public/career_path_assessment.html"
