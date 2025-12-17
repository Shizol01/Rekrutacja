from django import template

register = template.Library()

@register.filter
def minutes_to_hm(value):
    if value is None:
        return "—"
    try:
        value = int(value)
    except (TypeError, ValueError):
        return "—"

    hours = value // 60
    minutes = value % 60
    return f"{hours}h {minutes:02d}m"
