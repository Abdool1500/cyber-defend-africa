from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.courses.models import Course, CourseModule, Lesson

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

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
