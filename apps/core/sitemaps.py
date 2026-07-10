from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.courses.models import Course
from apps.resources.models import ResourcePost


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return [
            "core:home", "company:about", "company:solutions", "company:gpt_sentinel",
            "company:services", "academy:home", "courses:list", "resources:list",
            "leads:contact", "leads:waitlist", "career_path_assessment",
        ]

    def location(self, item):
        return reverse(item)


class CourseSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return Course.objects.filter(status=Course.Status.PUBLISHED)

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at


class ResourceSitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return ResourcePost.objects.filter(status=ResourcePost.Status.PUBLISHED)

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at
