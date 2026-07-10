from django.urls import path

from . import instructor_views as views

app_name = "instructor_quizzes"

urlpatterns = [
    path("", views.quiz_list, name="list"),
    path("new/", views.quiz_create, name="create"),
    path("<uuid:quiz_id>/edit/", views.quiz_edit, name="edit"),
    path("<uuid:quiz_id>/questions/add/", views.quiz_add_question, name="add_question"),
    path("<uuid:quiz_id>/questions/<uuid:quiz_question_id>/remove/", views.quiz_remove_question, name="remove_question"),
    path("<uuid:quiz_id>/random-rules/add/", views.quiz_add_random_rule, name="add_random_rule"),
    path("<uuid:quiz_id>/random-rules/<uuid:rule_id>/remove/", views.quiz_remove_random_rule, name="remove_random_rule"),
    path("<uuid:quiz_id>/publish/", views.quiz_publish, name="publish"),
    path("<uuid:quiz_id>/unpublish/", views.quiz_unpublish, name="unpublish"),
]
