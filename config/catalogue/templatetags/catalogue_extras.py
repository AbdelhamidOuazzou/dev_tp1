from django import template
from datetime import timedelta
from decimal import Decimal

register = template.Library()

@register.filter
def add_days(date, days):
    """Add a number of days to a date."""
    try:
        return date + timedelta(days=int(days))
    except (ValueError, TypeError):
        return date

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return ''

@register.filter
def sum_options(options):
    """Calculate the total sum of all options"""
    try:
        return sum(Decimal(str(option.option.prix)) * Decimal(str(option.quantite)) for option in options)
    except (ValueError, TypeError):
        return Decimal('0') 