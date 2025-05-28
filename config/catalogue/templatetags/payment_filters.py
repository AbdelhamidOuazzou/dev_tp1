from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sum_completed_payments(paiements):
    """Calculate the sum of completed payments."""
    return sum(p.montant for p in paiements if p.statut == 'complete')

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except (ValueError, TypeError):
        return value 