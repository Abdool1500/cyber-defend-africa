from django import template

register = template.Library()


@register.filter
def initials(full_name):
    """First letter of up to the first two words of a name, for a
    generated avatar badge (e.g. "Umar Aliyu" -> "UA")."""
    if not full_name:
        return "?"
    parts = [p for p in full_name.strip().split() if p]
    if not parts:
        return "?"
    return "".join(p[0] for p in parts[:2]).upper()


@register.filter
def duration_hm(total_seconds):
    """Seconds -> "Xh Ym" display (e.g. 5425 -> "1h 30m"), for learning
    time widgets. 0 renders as "0m" rather than an empty string."""
    total_seconds = int(total_seconds or 0)
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
