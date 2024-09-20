from django.shortcuts import get_object_or_404
from ninja import Query, Router

from exako.apps.card.api import schema
from exako.apps.card.models import Card, CardSet
from exako.apps.core import schema as core_schema
from exako.apps.term.models import Term
from exako.apps.user.auth.token import AuthBearer

card_router = Router(tags=['Cartão'], auth=AuthBearer())


@card_router.post(
    path='/set',
    response={201: schema.CardSetSchemaView, 401: core_schema.NotAuthenticated},
    summary='Criação de um conjunto de cartões de aprendizado.',
    description='Endpoint utilizado para criar um conjunto de cartões de aprendizado de um usuário.',
)
def create_cardset(
    request,
    cardset_schema: schema.CardSetSchema,
):
    return 201, CardSet.objects.create(
        user=request.user,
        **cardset_schema.model_dump(),
    )


@card_router.get(
    path='/set/{cardset_id}',
    response={
        200: schema.CardSetSchemaView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Consulta sobre um conjunto específico de cartões de aprendizado.',
    description='Endpoint utilizado para consultar um conjunto específico de cartões de aprendizado de um usuário.',
)
def get_cardset(request, cardset_id: int):
    return get_object_or_404(CardSet, id=cardset_id, user=request.user)


@card_router.get(
    path='/set',
    response={200: list[schema.CardSetSchemaView], 401: core_schema.NotAuthenticated},
    summary='Consulta sobre os conjuntos de cartões de aprendizado.',
    description='Endpoint utilizado para consultar todos os conjunto de cartões de aprendizado de um usuário.',
)
def list_cardset(
    request,
    filter_schema: schema.CardSetList = Query(),
):
    return CardSet.objects.filter(
        filter_schema.get_filter_expression(),
        user=request.user,
    )


@card_router.patch(
    path='/set/{cardset_id}',
    response={
        200: schema.CardSetSchemaView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Consulta sobre um conjunto específico de cartões de aprendizado.',
    description='Endpoint utilizado para consultar um conjunto específico de cartões de aprendizado de um usuário.',
)
def update_cardset(
    request,
    cardset_id: int,
    cardset_schema: schema.CardSetSchemaUpdate,
):
    cardset = get_object_or_404(
        CardSet,
        id=cardset_id,
        user=request.user,
    )

    for key, value in cardset_schema.model_dump(exclude_none=True).items():
        setattr(cardset, key, value)
    cardset.save()
    return cardset


@card_router.delete(
    path='/set/{cardset_id}',
    response={
        204: None,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Deleta um conjunto específico de cartões de aprendizado.',
    description='Endpoint utilizado para deletar um conjunto específico de cartões de aprendizado de um usuário.',
)
def delete_cardset(
    request,
    cardset_id: int,
):
    cardset = get_object_or_404(
        CardSet,
        id=cardset_id,
        user=request.user,
    )

    cardset.delete()
    return 204, None


@card_router.post(
    path='',
    response={
        201: schema.CardSchemaView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Cria um cartão de aprendizado.',
    description='Endpoint utilizado para criar um cartão de aprendizado de um conjunto de cartões específico.',
)
def create_card(
    request,
    card_schema: schema.CardSchema,
):
    get_object_or_404(
        CardSet,
        id=card_schema.cardset_id,
        user=request.user,
    )
    term = get_object_or_404(
        Term.objects.get(
            expression=card_schema.expression,
            language=card_schema.language,
        )
    )

    return 201, Card.objects.create(
        term=term,
        **card_schema.model_dump(exclude={'expression', 'language'}),
    )


@card_router.get(
    path='{card_id}',
    response={
        200: schema.CardSchemaView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Consulta de cartões de aprendizado.',
    description='Endpoint utilizado para consultar cartões.',
)
def get_card(request, card_id: int):
    return get_object_or_404(Card, id=card_id, cardset__user=request.user)


@card_router.get(
    path='/set/cards/{cardset_id}',
    response={
        200: list[schema.CardSchemaView],
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Consulta de cartões de aprendizado de um conjunto específico.',
    description='Endpoint utilizado para consultar os cartões de aprendizado de um determinado conjunto de cartões.',
)
def list_cards(
    request,
    cardset_id: int,
    filter_schema: schema.CardList = Query(),
):
    get_object_or_404(
        CardSet,
        id=cardset_id,
        user=request.user,
    )

    return Card.objects.filter(
        filter_schema.get_filter_expression(),
        cardset_id=cardset_id,
    )


@card_router.patch(
    path='/{card_id}/',
    response={
        200: schema.CardSchemaView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Atualiza cartões de aprendizado.',
    description='Endpoint utilizado para atualizar um cartão de aprendizado específico.',
)
def update_card(
    request,
    card_id: int,
    card_schema: schema.CardSchemaUpdate,
):
    card = get_object_or_404(Card, id=card_id, cardset__user=request.user)

    for key, value in card_schema.model_dump(exclude_none=True).items():
        setattr(card, key, value)
    card.save()
    return card


@card_router.delete(
    path='/{card_id}/',
    response={
        204: None,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Deleta cartões de aprendizado.',
    description='Endpoint utilizado para deleta um cartão de aprendizado específico.',
)
def delete_card(
    request,
    card_id: int,
):
    card = get_object_or_404(Card, id=card_id, cardset__user=request.user)
    card.delete()
    return 204, None
