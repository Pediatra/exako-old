from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.errors import HttpError

from exako.apps.core import schema as core_schema
from exako.apps.core.permissions import is_admin, permission_required
from exako.apps.term import constants
from exako.apps.term.api import schema
from exako.apps.term.models import TermDefinition, TermDefinitionTranslation
from exako.apps.user.auth.token import AuthBearer

definition_router = Router()


@definition_router.post(
    path='',
    response={
        201: schema.TermDefinitionView,
        401: core_schema.NotAuthenticated,
        403: core_schema.PermissionDenied,
        404: core_schema.NotFound,
    },
    summary='Criação das definições de um termo.',
    description='Endpoint utilizado para criar uma definição de um certo termo de um determinado idioma.',
    auth=AuthBearer(),
    openapi_extra={
        'responses': {
            409: {
                'description': 'A definição já existe para esse termo.',
                'content': {
                    'application/json': {
                        'example': {'detail': 'definition already exists to this term.'}
                    }
                },
            },
        }
    },
)
@permission_required([is_admin])
def create_definition(
    request,
    definition_schema: schema.TermDefinitionSchema,
):
    if TermDefinition.objects.filter(
        term_id=definition_schema.term,
        part_of_speech=definition_schema.part_of_speech,
        definition__ct=definition_schema.definition,
    ).exists():
        raise HttpError(
            status_code=409, message='definition already exists to this term.'
        )
    return 201, TermDefinition.objects.create(**definition_schema.model_dump())


@definition_router.post(
    path='/translation',
    response={
        201: schema.TermDefinitionTranslationView,
        401: core_schema.NotAuthenticated,
        403: core_schema.PermissionDenied,
        404: core_schema.NotFound,
    },
    summary='Criação da tradução das definições de um termo.',
    description='Endpoint utilizado para criar uma tradução para uma definição de um certo termo de um determinado idioma.',
    auth=AuthBearer(),
    openapi_extra={
        'responses': {
            409: {
                'description': 'A tradução nesse idioma enviada para essa definição já existe.',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'translation language for this definition is already registered.'
                        }
                    }
                },
            },
        }
    },
)
@permission_required([is_admin])
def create_definition_translation(
    request,
    translation_schema: schema.TermDefinitionTranslationSchema,
):
    try:
        return 201, TermDefinitionTranslation.objects.create(
            **translation_schema.model_dump()
        )
    except IntegrityError:
        raise HttpError(
            status_code=409,
            message='translation language for this definition is already registered.',
        )


@definition_router.get(
    path='',
    response={200: list[schema.TermDefinitionView]},
    summary='Consulta das definições de um termo.',
    description='Endpoint utilizado para consultar as definição de um certo termo de um determinado idioma.',
)
def list_definition(
    request,
    query_filter: schema.ListTermDefintionFilter = Query(),
):
    return TermDefinition.objects.filter(query_filter.get_filter_expression())


@definition_router.get(
    path='/translation/{term_definition}/{language}',
    response={
        200: schema.TermDefinitionTranslationView,
        404: core_schema.NotFound,
    },
    summary='Consulta a tradução da definição de um termo.',
    description='Endpoint utilizado para consultar a tradução das definições de um certo termo de um determinado idioma.',
)
def get_definition_translation(
    request,
    term_definition: int,
    language: constants.Language,
):
    return get_object_or_404(
        TermDefinitionTranslation,
        term_definition_id=term_definition,
        language=language,
    )
