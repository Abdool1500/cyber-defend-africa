from django.shortcuts import get_object_or_404, render

from .models import ResourcePost


def resource_list(request):
    posts = ResourcePost.objects.filter(status=ResourcePost.Status.PUBLISHED).select_related("category", "author")
    return render(request, "public/resource_list.html", {"posts": posts})


def resource_detail(request, slug):
    post = get_object_or_404(ResourcePost, slug=slug, status=ResourcePost.Status.PUBLISHED)
    return render(request, "public/resource_detail.html", {"post": post})
