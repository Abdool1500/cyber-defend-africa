import uuid

from django.db import models
from django.urls import reverse


class Course(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    estimated_duration = models.CharField(max_length=100, blank=True)
    thumbnail_path = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("courses:detail", kwargs={"slug": self.slug})


class CourseModule(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLISHED)

    class Meta:
        ordering = ["course", "display_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "display_order"], name="unique_module_order_per_course"
            )
        ]

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class Lesson(models.Model):
    class LessonType(models.TextChoices):
        VIDEO = "video", "Video"
        READING = "reading", "Reading"
        LAB = "lab", "Lab"
        LIVE = "live", "Live Session"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220)
    content = models.TextField(blank=True)
    video_url = models.URLField(null=True, blank=True)
    resource_path = models.CharField(max_length=500, null=True, blank=True)
    lesson_type = models.CharField(max_length=20, choices=LessonType.choices, default=LessonType.READING)
    display_order = models.PositiveIntegerField(default=0)
    estimated_minutes = models.PositiveIntegerField(default=15)
    is_preview = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLISHED)

    class Meta:
        ordering = ["module", "display_order"]
        constraints = [
            models.UniqueConstraint(fields=["module", "slug"], name="unique_lesson_slug_per_module")
        ]

    def __str__(self):
        return f"{self.module.title} — {self.title}"
