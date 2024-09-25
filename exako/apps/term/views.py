import re

from django.core.paginator import Paginator
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.urls import reverse_lazy

from exako.apps.term.constants import (
    Language,
    TermLexicalType,
    language_alphabet_map,
    language_emoji_map,
)
from exako.apps.term.models import (
    Term,
    TermDefinition,
    TermExampleLink,
    TermLexical,
    TermPronunciation,
)


def term_home(request):
    languages = {}
    for code, name in Language.choices:
        languages[name] = {
            'code': code,
            'emoji': language_emoji_map.get(code),
            'count': Term.objects.filter(language=code).count(),
        }
    return render(
        request,
        'term/term_home.html',
        context={'languages': languages},
    )


def language_view(request, language):
    return render(
        request,
        'term/language_view.html',
        context={
            'alphabet': list(language_alphabet_map.get(language)),
            'language': language,
            'languages': dict(Language.choices),
        },
    )


def term_view(request, language):
    expression = request.GET.get('expression')
    if not expression:
        return redirect('/')
    term = Term.objects.get(expression=expression, language=language)
    if not term:
        return redirect('/')
    lexical = request.GET.get('lexical')
    if lexical:
        return term_lexical_view(request, term, lexical)
    term_definitions = TermDefinition.objects.filter(term=term)
    term_definition_examples = TermExampleLink.objects.select_related(
        'term_example'
    ).filter(term_definition_id__in=term_definitions.values('id'))
    term_pronunciation = TermPronunciation.objects.get(term=term)
    return render(
        request,
        'term/term_view.html',
        context={
            'term': term,
            'term_definitions': term_definitions,
            'term_definition_examples': term_definition_examples,
            'term_pronunciation': term_pronunciation,
            'languages': [
                (code, name) for code, name in Language.choices if code != language
            ],
        },
    )


def term_lexical_view(request, term, term_lexical):
    term_lexical = TermLexical.objects.filter(term=term, value=term_lexical).first()
    if term_lexical is None:
        return redirect('/')
    term_definitions = TermDefinition.objects.filter(term_lexical=term_lexical)
    term_definition_examples = TermExampleLink.objects.select_related(
        'term_example'
    ).filter(term_definition_id__in=term_definitions.values('id'))
    term_pronunciation = TermPronunciation.objects.get(term_lexical=term_lexical)
    return render(
        request,
        'term/term_lexical_view.html',
        context={
            'term': term,
            'term_lexical': term_lexical,
            'term_definitions': term_definitions,
            'term_definition_examples': term_definition_examples,
            'term_pronunciation': term_pronunciation,
            'languages': [
                (code, name) for code, name in Language.choices if code != term.language
            ],
        },
    )


def search_term_partial(request):
    expression = request.POST.get('expression') or request.GET.get('expression')
    language = request.POST.get('language') or request.GET.get('language')
    if not all([expression, language]):
        return HttpResponse(status=204)
    query = (
        Term.objects.search(
            expression=expression,
            language=language,
        )
        .order_by('expression')
        .values_list('expression', flat=True)
    )
    paginator = Paginator(query, per_page=8)
    page = paginator.page(request.GET.get('page', 1))
    return render(
        request,
        'term/partials/search.html',
        context={
            'page': page,
            'page_count': paginator.num_pages,
            'target': '#results-area',
            'prev_url': (
                f'{reverse_lazy("term:search")}?expression={expression}&language={language}'
            ),
            'next_url': (
                f'{reverse_lazy("term:search")}?expression={expression}&language={language}'
            ),
        },
    )


def search_reverse_partial(request):
    expression = request.POST.get('expression') or request.GET.get('expression')
    language = request.POST.get('language') or request.GET.get('language')
    translation_language = request.POST.get('translation_language') or request.GET.get(
        'translation_language'
    )
    if not all([expression, language, translation_language]):
        return HttpResponse(status=204)
    query = (
        Term.objects.search_reverse(
            expression=expression,
            language=language,
            translation_language=translation_language,
        )
        .order_by('expression')
        .values_list('expression', flat=True)
    )
    paginator = Paginator(query, per_page=8)
    page = paginator.page(request.GET.get('page', 1))
    return render(
        request,
        'term/partials/search.html',
        context={
            'page': page,
            'page_count': paginator.num_pages,
            'target': '#reverse-results-area',
            'prev_url': (
                f'{reverse_lazy("term:search_reverse")}?expression={expression}&language={language}&translation_language={translation_language}'
            ),
            'next_url': (
                f'{reverse_lazy("term:search_reverse")}?expression={expression}&language={language}&translation_language={translation_language}'
            ),
        },
    )


def index_term_partial(request):
    char = request.POST.get('char') or request.GET.get('char')
    language = request.POST.get('language') or request.GET.get('language')
    if not all([char, language]) and not re.match(char, r'^[a-zA-Z]$'):
        return HttpResponse(status=204)
    query = Term.objects.filter(
        language=language,
        expression__startswith=char.lower(),
    ).order_by('expression')
    paginator = Paginator(query, per_page=28)
    page = paginator.page(request.GET.get('page', 1))
    return render(
        request,
        'term/partials/index.html',
        context={
            'page': page,
            'char': char,
            'prev_url': f'{reverse_lazy("term:index")}?char={char}&language={language}',
            'next_url': f'{reverse_lazy("term:index")}?char={char}&language={language}',
        },
    )


def term_examples_partial(request, language):
    link_objects = {
        'term': Term,
        'term_definition': TermDefinition,
        'term_lexical': TermLexical,
    }
    obj = None
    identifier = None
    for key, value in request.GET.items():
        Model = link_objects.get(key)
        if Model is None:
            continue
        obj = get_object_or_404(Model, id=value)
        identifier = key
    if obj is None:
        return HttpResponse(status=204)
    query = (
        TermExampleLink.objects.select_related('term_example')
        .filter(**{identifier: obj})
        .order_by('id')
    )
    paginator = Paginator(query, per_page=4)
    page = paginator.page(request.GET.get('page', 1))
    return render(
        request,
        'term/partials/term_examples.html',
        context={
            **{identifier: obj},
            'language': language,
            'page': page,
            'next_url': f"{reverse_lazy('term:term_examples', kwargs={'language': language})}?{identifier}={obj.id}",
        },
    )


def term_lexicals_partial(request, term_id):
    term = get_object_or_404(Term, id=term_id)
    lexical_type = request.GET.get('lexical_type')
    if not lexical_type:
        return HttpResponse(status=204)
    term_lexicals = (
        TermLexical.objects.select_related('term_value_ref')
        .filter(term=term, type=lexical_type)
        .order_by('id')
    )
    return render(
        request,
        'term/partials/term_lexicals.html',
        context={
            'term': term,
            'term_lexicals': term_lexicals,
            'lexical_type': TermLexicalType(int(lexical_type)),
        },
    )
