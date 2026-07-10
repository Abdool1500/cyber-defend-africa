from django.urls import path

from . import views

app_name = "instructor_question_bank"

urlpatterns = [
    path("", views.question_list, name="list"),
    path("new/", views.question_create, name="create"),
    path("<uuid:question_id>/", views.question_preview, name="preview"),
    path("<uuid:question_id>/edit/", views.question_edit, name="edit"),
    path("<uuid:question_id>/duplicate/", views.question_duplicate, name="duplicate"),
    path("<uuid:question_id>/archive/", views.question_archive, name="archive"),
    path("<uuid:question_id>/restore/", views.question_restore, name="restore"),
]
