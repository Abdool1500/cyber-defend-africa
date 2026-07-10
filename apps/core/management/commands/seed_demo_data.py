from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.courses.models import Course, CourseModule, Lesson
from apps.question_bank.models import Question, QuestionOption
from apps.quizzes.models import Quiz, QuizQuestion

COURSES = [
    {
        "title": "AI Security Engineering",
        "slug": "ai-security-engineering",
        "short_description": "Learn to understand, secure, assess, and responsibly build AI-enabled systems.",
        "description": (
            "AI Security Engineering is a hands-on program covering the security of AI and "
            "LLM-enabled systems — from foundations through secure development, red teaming, "
            "and governance."
        ),
        "category": "AI Security",
        "level": Course.Level.INTERMEDIATE,
        "estimated_duration": "12 weeks, self-paced",
        "modules": [
            "AI and Machine Learning Foundations",
            "Cybersecurity Foundations for AI",
            "AI Threat Landscape",
            "Secure AI Development & LLM Security Fundamentals",
            "AI Application & API Security",
            "AI Red Teaming & Security Testing",
            "AI Governance & Responsible AI",
            "Capstone Project",
        ],
    },
    {
        "title": "Ethical Hacking & Penetration Testing",
        "slug": "ethical-hacking",
        "short_description": "Master offensive security fundamentals through hands-on, controlled labs.",
        "description": (
            "A practical penetration testing program covering reconnaissance, vulnerability "
            "assessment, web application security, and professional reporting — grounded in "
            "responsible disclosure practices."
        ),
        "category": "Offensive Security",
        "level": Course.Level.INTERMEDIATE,
        "estimated_duration": "12 weeks, self-paced",
        "modules": [
            "Cybersecurity & Networking Foundations",
            "Linux for Security",
            "Reconnaissance & Information Gathering",
            "Scanning, Enumeration & Vulnerability Assessment",
            "Web Application Security & OWASP Top 10",
            "Exploitation Tooling (Nmap, Wireshark, Burp Suite, Metasploit)",
            "Penetration Testing Methodology & Reporting",
            "Capstone Project",
        ],
    },
    {
        "title": "SOC Analyst & Blue Team Operations",
        "slug": "soc-analyst",
        "short_description": "Build practical skills in detection, triage, and incident response.",
        "description": (
            "A defensive security program covering SOC fundamentals, log analysis, threat "
            "detection, and incident response — preparing analysts for real security "
            "operations work."
        ),
        "category": "Defensive Security",
        "level": Course.Level.BEGINNER,
        "estimated_duration": "10 weeks, self-paced",
        "modules": [
            "SOC Fundamentals & Security Operations",
            "Networking, Windows & Linux Security Fundamentals",
            "Log Analysis & SIEM Fundamentals",
            "Alert Triage & Incident Investigation",
            "Threat Detection, Phishing & Malware Fundamentals",
            "Network Traffic Analysis & MITRE ATT&CK",
            "Threat Intelligence & Incident Response",
            "Capstone Project",
        ],
    },
]


class Command(BaseCommand):
    help = "Seed demo data: the three flagship courses with modules and sample lessons."

    @transaction.atomic
    def handle(self, *args, **options):
        for course_data in COURSES:
            course, created = Course.objects.update_or_create(
                slug=course_data["slug"],
                defaults={
                    "title": course_data["title"],
                    "short_description": course_data["short_description"],
                    "description": course_data["description"],
                    "category": course_data["category"],
                    "level": course_data["level"],
                    "estimated_duration": course_data["estimated_duration"],
                    "status": Course.Status.PUBLISHED,
                    "published_at": timezone.now(),
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} course: {course.title}")

            for order, module_title in enumerate(course_data["modules"], start=1):
                module, _ = CourseModule.objects.update_or_create(
                    course=course,
                    display_order=order,
                    defaults={"title": module_title, "status": CourseModule.Status.PUBLISHED},
                )
                Lesson.objects.update_or_create(
                    module=module,
                    slug="overview",
                    defaults={
                        "title": f"{module_title} — Overview",
                        "content": f"Introductory lesson covering the key concepts of {module_title}.",
                        "lesson_type": Lesson.LessonType.READING,
                        "display_order": 1,
                        "estimated_minutes": 20,
                        "is_preview": order == 1,
                        "status": Lesson.Status.PUBLISHED,
                    },
                )

            self._seed_sample_quiz(course)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    def _seed_sample_quiz(self, course):
        """One question of each type + a published quiz combining them,
        so every course has a working end-to-end quiz to demo/test with."""
        mc_question, _ = Question.objects.update_or_create(
            course=course, question_text=f"Which of these best describes {course.title}?",
            defaults={
                "topic": "Foundations", "question_type": Question.QuestionType.MULTIPLE_CHOICE,
                "difficulty": Question.Difficulty.EASY, "default_points": 1,
                "status": Question.Status.PUBLISHED,
                "explanation": "This introductory question checks basic course orientation.",
            },
        )
        if not mc_question.options.exists():
            QuestionOption.objects.create(question=mc_question, option_text="A hands-on cybersecurity course", is_correct=True, display_order=1)
            QuestionOption.objects.create(question=mc_question, option_text="A cooking class", is_correct=False, display_order=2)

        ms_question, _ = Question.objects.update_or_create(
            course=course, question_text="Select all topics covered in this course.",
            defaults={
                "topic": "Foundations", "question_type": Question.QuestionType.MULTIPLE_SELECT,
                "difficulty": Question.Difficulty.MEDIUM, "default_points": 2,
                "status": Question.Status.PUBLISHED,
            },
        )
        if not ms_question.options.exists():
            QuestionOption.objects.create(question=ms_question, option_text=course.category, is_correct=True, display_order=1)
            QuestionOption.objects.create(question=ms_question, option_text="Practical labs", is_correct=True, display_order=2)
            QuestionOption.objects.create(question=ms_question, option_text="Unrelated cuisine techniques", is_correct=False, display_order=3)

        tf_question, _ = Question.objects.update_or_create(
            course=course, question_text=f"{course.title} includes hands-on practical labs.",
            defaults={
                "topic": "Foundations", "question_type": Question.QuestionType.TRUE_FALSE,
                "difficulty": Question.Difficulty.EASY, "default_points": 1,
                "status": Question.Status.PUBLISHED,
            },
        )
        if not tf_question.options.exists():
            QuestionOption.objects.create(question=tf_question, option_text="True", is_correct=True, display_order=1)
            QuestionOption.objects.create(question=tf_question, option_text="False", is_correct=False, display_order=2)

        sa_question, _ = Question.objects.update_or_create(
            course=course, question_text="In one or two sentences, describe a key skill you expect to gain from this course.",
            defaults={
                "topic": "Foundations", "question_type": Question.QuestionType.SHORT_ANSWER,
                "difficulty": Question.Difficulty.MEDIUM, "default_points": 2,
                "status": Question.Status.PUBLISHED,
                "grading_guidance": "Award full points for any relevant, course-related skill.",
            },
        )

        quiz, _ = Quiz.objects.update_or_create(
            course=course, title=f"{course.title} — Foundations Check",
            defaults={
                "description": "A short quiz covering the foundational module of this course.",
                "instructions": "Answer all questions. Short-answer responses are reviewed manually.",
                "status": Quiz.Status.PUBLISHED,
                "attempt_limit": 3,
                "passing_score": 60,
                "shuffle_questions": True,
                "shuffle_options": True,
                "show_score_after_submission": True,
                "show_correct_answers": True,
                "show_explanations": True,
            },
        )
        for order, question in enumerate([mc_question, ms_question, tf_question, sa_question], start=1):
            QuizQuestion.objects.update_or_create(quiz=quiz, question=question, defaults={"display_order": order})
