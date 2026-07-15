"""Net Promoter Score calculation from StudentFeedback.nps_score.

Standard NPS methodology: respondents scoring 9-10 are Promoters,
7-8 are Passives, 0-6 are Detractors. NPS = %Promoters - %Detractors,
expressed as a whole number from -100 to 100. This lives in
apps.analytics rather than apps.feedback so it can be reused by
course-level (instructor) and platform-wide (management) reporting
without either app depending on the other's view layer.
"""


def calculate_nps(feedback_queryset):
    """Returns a dict of promoters/passives/detractors/nps_score/total_responses
    for the given StudentFeedback queryset. nps_score is None when there
    are no responses, rather than 0, so callers can distinguish "no data"
    from "NPS is exactly zero"."""
    scores = list(feedback_queryset.values_list("nps_score", flat=True))
    total = len(scores)

    result = {
        "total_responses": total,
        "promoters": 0,
        "passives": 0,
        "detractors": 0,
        "promoter_pct": None,
        "passive_pct": None,
        "detractor_pct": None,
        "nps_score": None,
    }

    if total == 0:
        return result

    promoters = sum(1 for s in scores if s >= 9)
    passives = sum(1 for s in scores if 7 <= s <= 8)
    detractors = sum(1 for s in scores if s <= 6)

    result["promoters"] = promoters
    result["passives"] = passives
    result["detractors"] = detractors
    result["promoter_pct"] = round(promoters / total * 100, 1)
    result["passive_pct"] = round(passives / total * 100, 1)
    result["detractor_pct"] = round(detractors / total * 100, 1)
    result["nps_score"] = round((promoters / total * 100) - (detractors / total * 100))

    return result
