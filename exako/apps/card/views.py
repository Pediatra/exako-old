from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy

from exako.apps.card.forms import CardSetForm
from exako.apps.card.models import Card, CardSet
from exako.apps.term.constants import Language
from exako.apps.term.models import Term, TermDefinitionTranslation
from exako.apps.user.auth.decorator import login_required


def cardset_home_view(request):
    return render(request, 'card/cardset_home.html')


@login_required
def list_cardset_partial(request):
    name = request.GET.get('name')
    cardsets = (
        CardSet.objects.filter(user=request.user)
        .annotate(card_count=Count('card'))
        .order_by('-pinned', 'created_at')
    )
    if name:
        cardsets = cardsets.filter(name__ct_icontains=name)
    return render(
        request, 'card/partials/cardset_list.html', context={'cardsets': cardsets}
    )


@login_required
def create_cardset_partial(request):
    if request.method == 'POST':
        form = CardSetForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse()
            response.status_code = 302
            response.headers['HX-Redirect'] = reverse_lazy('card:cardset_home')
            return response
    else:
        form = CardSetForm()
    return render(
        request,
        'card/partials/cardset_change.html',
        context={
            'form': form,
            'post_url': reverse_lazy('card:create_cardset'),
        },
    )


@login_required
def update_cardset_partial(request, cardset_id):
    cardset = get_object_or_404(CardSet, user=request.user, id=cardset_id)
    if request.method == 'POST':
        form = CardSetForm(request.POST, instance=cardset)
        if form.is_valid():
            form.save()
            response = HttpResponse()
            response.status_code = 302
            response.headers['HX-Redirect'] = reverse_lazy('card:cardset_home')
            return response
    else:
        form = CardSetForm(instance=cardset)
    return render(
        request,
        'card/partials/cardset_change.html',
        context={
            'form': form,
            'post_url': reverse_lazy(
                'card:update_cardset', kwargs={'cardset_id': cardset_id}
            ),
        },
    )


@login_required
def add_cardset_partial(request, cardset_id):
    cardset = get_object_or_404(CardSet, user=request.user, id=cardset_id)
    return render(
        request,
        'card/partials/add/search.html',
        context={
            'cardset': cardset,
            'languages': dict(Language.choices),
        },
    )


@login_required
def add_cardset_search_partial(request, cardset_id):
    expression = request.POST.get('expression') or request.GET.get('expression')
    language = request.POST.get('language') or request.GET.get('language')
    if not all([expression, language]):
        return HttpResponse(status=204)
    query = Term.objects.search(
        expression=expression,
        language=language,
    ).order_by('expression')
    paginator = Paginator(query, per_page=8)
    page = paginator.page(request.GET.get('page', 1))
    return render(
        request,
        'card/partials/add/search_result.html',
        context={
            'page': page,
            'page_count': paginator.num_pages,
            'cardset_id': cardset_id,
            'prev_url': (
                f'{reverse_lazy("card:add_cardset_search", kwargs={"cardset_id": cardset_id})}?expression={expression}&language={language}'
            ),
            'next_url': (
                f'{reverse_lazy("card:add_cardset_search", kwargs={"cardset_id": cardset_id})}?expression={expression}&language={language}'
            ),
        },
    )


@login_required
def add_cardset_create_partial(request, cardset_id):
    term_id = request.GET.get('term_id') or request.POST.get('term_id')
    cardset = get_object_or_404(CardSet, user=request.user, id=cardset_id)
    term = get_object_or_404(Term, id=term_id)
    if request.method == 'POST':
        Card.objects.create(
            cardset=cardset,
            term=term,
            note=request.POST.get('note'),
        )
        response = HttpResponse()
        response.status_code = 302
        response.headers['HX-Redirect'] = request.GET.get('next')
        return response
    note_value = TermDefinitionTranslation.objects.filter(
        term_definition__term=term,
        language=request.user.native_language,
    ).values_list('meaning', flat=True)
    return render(
        request,
        'card/partials/add/create.html',
        context={
            'cardset': cardset,
            'term': term,
            'note_value': ','.join(note_value),
        },
    )


def cardset_view(request, cardset_id):
    return render(request, 'card/cardset_view.html', context={'cardset_id': cardset_id})


@login_required
def card_view_partial(request, cardset_id):
    cardset = get_object_or_404(CardSet, user=request.user, id=cardset_id)
    query = (
        Card.objects.select_related('term')
        .filter(cardset_id=cardset_id)
        .order_by('created_at')
        .distinct()
    )
    paginator = Paginator(query, per_page=1)
    page = paginator.page(request.GET.get('page', 1))
    if not page.object_list:
        response = HttpResponse()
        response.status_code = 302
        response.headers['HX-Redirect'] = reverse_lazy('card:cardset_home')
        return response
    return render(
        request,
        'card/partials/card_view.html',
        context={
            'cardset': cardset,
            'page': page,
            'cards': query,
            'percentage': int((page.number / paginator.num_pages) * 100),
            'card': page.object_list[0],
            'page_count': paginator.num_pages,
        },
    )


@login_required
def card_update_partial(request, cardset_id, card_id):
    cardset = get_object_or_404(CardSet, user=request.user, id=cardset_id)
    card = get_object_or_404(Card, cardset=cardset, id=card_id)
    if request.method == 'POST':
        card.note = request.POST.get('note')
        card.save()
        response = HttpResponse()
        response.status_code = 302
        response.headers['HX-Redirect'] = reverse_lazy(
            'card:cardset_view',
            kwargs={'cardset_id': cardset_id},
        )
        return response

    return render(
        request,
        'card/partials/card_update.html',
        context={'cardset': cardset, 'card': card},
    )
