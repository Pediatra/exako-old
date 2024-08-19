from django.db import IntegrityError
from django.db.models import OuterRef, Q, Subquery
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from fluentia.apps.core import schema as core_schema
from fluentia.apps.core.permissions import is_admin, permission_required
from fluentia.apps.term import constants
from fluentia.apps.term.api import schema
from fluentia.apps.term.models import (
    TermExample,
    TermExampleLink,
    TermExampleTranslation,
    TermExampleTranslationLink,
)
from fluentia.apps.user.auth.token import AuthBearer

example_router = Router()


@example_router.post(
    path='',
    response={
        201: schema.TermExampleView,
        401: core_schema.NotAuthenticated,
        403: core_schema.PermissionDenied,
        404: core_schema.NotFound,
    },
    summary='Criação de exemplos sobre um termo.',
    description="""
        Endpoint utilizado para criação de exemplos para termos ou definições.
        Não poderá constar exemplos repetidos em uma determinada linguagem, para isso se o exemplo enviado já exisitir ele será retornado e não criado.
        Só poderá ser enviado um dos 3 objetos para ligação com o exemplo fornecido.
        term - Exemplo para termos
        term_definition - Exemplo para definições
        term_lexical - Exemplo para lexical
    """,
    auth=AuthBearer(),
    openapi_extra={
        'responses': {
            409: {
                'description': 'Modelo já fornecido já está ligado com o exemplo específicada.',
                'content': {
                    'application/json': {
                        'example': {'detail': 'example already linked with this model.'}
                    }
                },
            },
        }
    },
)
@permission_required([is_admin])
def create_example(
    request,
    example_schema: schema.TermExampleSchema,
):
    example, _ = TermExample.objects.get_or_create(
        defaults=example_schema.model_dump(
            include={
                'level',
                'additional_content',
            }
        ),
        **example_schema.model_dump(
            include={
                'language',
                'example',
            }
        ),
    )

    try:
        TermExampleLink.objects.create(
            term_example_id=example.id,
            **example_schema.model_dump(
                include={
                    'highlight',
                    'term_example',
                    'term',
                    'term_definition',
                    'term_lexical',
                },
            ),
        )
    except IntegrityError:
        raise HttpError(
            status_code=409, message='example already linked with this model.'
        )

    return 201, {
        **model_to_dict(example),
        'highlight': example_schema.highlight,
    }


@example_router.post(
    path='/translation',
    response={
        201: schema.TermExampleTranslationView,
        401: core_schema.NotAuthenticated,
        403: core_schema.PermissionDenied,
        404: core_schema.NotFound,
    },
    summary='Criação de traduções para exemplos sobre um termo.',
    description="""
        Endpoint utilizado para criação tradução para exemplos de termos ou definições.
        Só poderá ser enviado um dos 3 objetos para ligação com o exemplo fornecido.
        expression, origin_language  - Exemplo para termos
        term_definition_id - Exemplo para definições
        term_lexical_id - Exemplo para lexical
    """,
    openapi_extra={
        'responses': {
            409: {
                'description': 'Modelo já fornecido já está ligado com a frase específicada.',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'the example is already linked with this model.'
                        }
                    }
                },
            },
        }
    },
    auth=AuthBearer(),
)
@permission_required([is_admin])
def create_example_translation(
    request,
    translation_schema: schema.TermExampleTranslationSchema,
):
    if TermExampleTranslation.objects.filter(
        language=translation_schema.language,
        translation__ct=translation_schema.translation,
        term_example_id=translation_schema.term_example,
    ).exists():
        raise HttpError(
            status_code=409, message='translation already exists for this example.'
        )

    translation = TermExampleTranslation.objects.create(
        **translation_schema.model_dump(
            include={
                'language',
                'term_example',
                'translation',
                'additional_content',
            }
        ),
    )

    TermExampleTranslationLink.objects.create(
        translation_language=translation_schema.language,
        **translation_schema.model_dump(
            exclude={'language', 'translation', 'additional_content'},
            exclude_none=True,
        ),
    )

    return 201, {
        **model_to_dict(translation),
        'highlight': translation_schema.highlight,
    }


@example_router.get(
    path='',
    response={200: list[schema.TermExampleView]},
    summary='Consulta de exemplos sobre um termo.',
    description='Endpoint utilizado para consultar exemplos de termos ou definições.',
)
@paginate(PageNumberPagination)
def list_example(
    request,
    example_link_schema: schema.TermExampleLinkSchema = Query(),
    level: constants.Level | None = Query(
        default=None, description='Filtrar pelo level.'
    ),
):
    return (
        TermExample.objects.filter(
            Q(level=level) if level else Q(),
            id__in=Subquery(
                TermExampleLink.objects.select_related('term')
                .filter(example_link_schema.get_filter_expression())
                .values('term_example_id')
            ),
        )
        .annotate(
            highlight=Subquery(
                TermExampleLink.objects.select_related('term')
                .filter(
                    example_link_schema.get_filter_expression(),
                    term_example_id=OuterRef('id'),
                )
                .values('highlight')
            )
        )
        .order_by('id')
    )


@example_router.get(
    path='/translation/{term_example}/{language}',
    response={
        200: schema.TermExampleTranslationView,
        404: core_schema.NotFound,
    },
    summary='Consulta da tradução dos exemplos.',
    description='Endpoint para consultar a tradução da tradução de um determinado exemplo.',
)
def get_example_translation(
    request,
    term_example: int,
    language: constants.Language,
    example_link_schema: schema.TermExampleLinkSchema = Query(),
):
    return get_object_or_404(
        TermExampleTranslation.objects.filter(
            term_example_id=term_example,
            language=language,
        ).annotate(
            highlight=Subquery(
                TermExampleTranslationLink.objects.select_related('term')
                .filter(
                    example_link_schema.get_filter_expression(),
                    term_example_id=OuterRef('term_example_id'),
                    translation_language=language,
                )
                .values('highlight')
            )
        )
    )
