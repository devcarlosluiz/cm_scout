from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def confidence_color(confidence: str) -> str:
    colors = {
        'high': 'text-green-400',
        'medium': 'text-yellow-400',
        'low': 'text-red-400',
    }
    return colors.get(confidence, 'text-gray-400')


@register.filter
def confidence_bg(confidence: str) -> str:
    colors = {
        'high': 'bg-green-500/20 text-green-400 border border-green-500/30',
        'medium': 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
        'low': 'bg-red-500/20 text-red-400 border border-red-500/30',
    }
    return colors.get(confidence, 'bg-gray-500/20 text-gray-400')


@register.filter
def confidence_label(confidence: str) -> str:
    labels = {
        'high': 'Alta',
        'medium': 'Média',
        'low': 'Baixa',
    }
    return labels.get(confidence, confidence)


@register.filter
def odd_color(odd_value) -> str:
    try:
        val = float(odd_value)
        if val >= 3.0:
            return 'text-green-400'
        elif val >= 1.8:
            return 'text-yellow-400'
        return 'text-gray-300'
    except (ValueError, TypeError):
        return 'text-gray-300'


@register.simple_tag
def time_until(dt) -> str:
    now = timezone.now()
    diff = dt - now
    if diff.days > 0:
        return f'em {diff.days}d'
    hours = diff.seconds // 3600
    if hours > 0:
        return f'em {hours}h'
    minutes = diff.seconds // 60
    return f'em {minutes}min'
