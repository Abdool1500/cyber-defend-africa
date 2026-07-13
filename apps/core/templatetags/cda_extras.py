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
