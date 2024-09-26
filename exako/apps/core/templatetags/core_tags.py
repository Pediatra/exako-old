from django.utils.translation import gettext as _
from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def simplified_timesince(value):
    now = timezone.now()
    diff = now - value

    if diff < timedelta(minutes=1):
        return _('agora')
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        return _('{} minuto atrás').format(minutes) if minutes == 1 else _('{} minutos atrás').format(minutes)
    elif diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return _('{} hora atrás').format(hours) if hours == 1 else _('{} horas atrás').format(hours)
    elif diff < timedelta(days=30):
        days = diff.days
        return _('{} dia atrás').format(days) if days == 1 else _('{} dias atrás').format(days)
    elif diff < timedelta(days=365):
        months = diff.days // 30
        return _('{} mês atrás').format(months) if months == 1 else _('{} meses atrás').format(months)
    else:
        years = diff.days // 365
        return _('{} ano atrás').format(years) if years == 1 else _('{} anos atrás').format(years)
