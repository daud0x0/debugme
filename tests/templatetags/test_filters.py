from django import template

register = template.Library()

@register.filter
def filter_correct(questions):
    """Filter to get only correct answers"""
    return [q for q in questions if q.is_correct]

@register.filter
def filter_incorrect(questions):
    """Filter to get only incorrect answers"""
    return [q for q in questions if not q.is_correct]

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return '' 