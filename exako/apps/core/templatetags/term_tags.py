from django import template
import string

from django.utils.safestring import mark_safe
from django.urls import reverse_lazy

from exako.apps.term.models import Term

register = template.Library()


@register.filter(is_safe=True)
def term_reference(value, language):
    parts = value.translate(str.maketrans('', '', string.punctuation)).split()
    query = Term.objects.filter(language=language, expression__in=parts)
    expression_values = [term.expression.lower() for term in query]

    new_value = ''
    for part in value.split():
        unpunctuation_part = part.translate(str.maketrans('', '', string.punctuation))
        if unpunctuation_part.lower() in expression_values:
            punctuation = part.replace(unpunctuation_part, '')
            part = f'<a href="{reverse_lazy("term:view", kwargs={"language": language})}?expression={unpunctuation_part}">{unpunctuation_part}</a>'
            new_value += part + punctuation + ' '
        else:
            new_value += part + ' '

    return mark_safe(new_value)


@register.filter(is_safe=True)
def highlight_sentence(value, highlight):
    result = ''
    start = 0
    for begin, end in highlight:
        result += value[start:begin] + '<strong>' + value[begin:end] + '</strong>'
        start = end
    result += value[start:]
    return mark_safe(result)
