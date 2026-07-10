from django.urls import path

from . import student_views as views

app_name = "student_quizzes"

urlpatterns = [
    path("quizzes/", views.quiz_list, name="list"),
    path("quizzes/<uuid:quiz_id>/", views.quiz_detail, name="detail"),
    path("quizzes/<uuid:quiz_id>/start/", views.quiz_start, name="start"),
    path("attempts/", views.attempt_list, name="attempt_list"),
    path("attempts/<uuid:attempt_id>/", views.attempt_detail, name="attempt"),
    path("attempts/<uuid:attempt_id>/results/", views.attempt_results, name="results"),
    path("attempts/<uuid:attempt_id>/answer/", views.save_answer_api, name="save_answer"),
    path("attempts/<uuid:attempt_id>/submit/", views.submit_attempt_api, name="submit_attempt"),
]
