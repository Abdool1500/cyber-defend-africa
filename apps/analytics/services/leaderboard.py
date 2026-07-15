"""Anonymized leaderboard position — a student only ever sees their own
rank/percentile, never another student's name or score, matching the
same anonymity posture already established for feedback (16.I) and
top-instructor rankings (16.J). Ranked by average graded quiz score,
the only metric every active student can be meaningfully compared on
regardless of which courses they're enrolled in.
"""
import math

from django.db.models import Avg

from apps.quizzes.models import QuizAttempt


def get_leaderboard_position(student):
    """Returns eligibility, this student's "Top X%" figure (lower is
    better — the single best-scoring student is "Top 1%"), and how many
    students were ranked. A student with no graded quiz attempts isn't
    ranked at all — there's nothing to compare."""
    rankings = list(
        QuizAttempt.objects.filter(status=QuizAttempt.Status.GRADED)
        .values("student_id")
        .annotate(avg_score=Avg("percentage"))
        .order_by("-avg_score")
    )
    total_ranked = len(rankings)
    student_ids_in_order = [row["student_id"] for row in rankings]

    if total_ranked == 0 or student.id not in student_ids_in_order:
        return {"eligible": False, "top_percentage": None, "total_ranked": total_ranked}

    position = student_ids_in_order.index(student.id) + 1  # 1-indexed rank, 1 = best
    top_percentage = math.ceil((position / total_ranked) * 100)

    return {"eligible": True, "top_percentage": top_percentage, "total_ranked": total_ranked}
