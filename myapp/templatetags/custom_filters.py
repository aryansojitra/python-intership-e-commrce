from django import template

register = template.Library()

@register.filter(name='mul')
def multiply(value, arg):
    """Multiply the arg by the value."""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='currency')
def currency(value):
    """Format value as currency."""
    try:
        return f"₹{int(value):,}"
    except (ValueError, TypeError):
        return "₹0"
