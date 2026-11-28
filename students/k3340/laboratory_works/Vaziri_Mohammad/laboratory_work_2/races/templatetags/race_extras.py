from django import template

register = template.Library()


@register.filter
def laptime(value):
    """timedelta -> «12:34.567» (минуты:секунды.миллисекунды)."""
    if value is None:
        return "—"
    total_ms = int(round(value.total_seconds() * 1000))
    minutes, rest = divmod(total_ms, 60_000)
    seconds, ms = divmod(rest, 1000)
    return f"{minutes}:{seconds:02d}.{ms:03d}"


@register.filter
def place_badge(position):
    """CSS-класс Bootstrap для призового места."""
    return {1: "bg-warning text-dark", 2: "bg-secondary", 3: "bg-danger"}.get(position, "bg-light text-dark border")
