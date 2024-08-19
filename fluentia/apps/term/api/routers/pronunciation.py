from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Query, Router
from ninja.errors import HttpError

from fluentia.apps.core import schema as core_schema
from fluentia.apps.core.permissions import is_admin, permission_required
from fluentia.apps.term.api import schema
from fluentia.apps.term.models import TermPronunciation
from fluentia.apps.user.auth.token import AuthBearer

pronunciation_router = Router()


@pronunciation_router.post(
    path='',
    response={
        201: schema.TermPronunciationView,
        401: core_schema.NotAuthenticated,
        403: core_schema.PermissionDenied,
        404: core_schema.NotFound,
    },
    summary='Criação de pronúncia.',
    description="""
        Endpoint utilizado para criar pronúncias com áudio, fonemas e descrição sobre um determinado objeto.
        Só poderá ser enviado um dos 3 objetos para ligação com a pronúncia específica.
        term - Pronúncia para termos
        term_example - Pronúncia para exemplos
        term_lexical - Pronúncia para lexical
    """,
    auth=AuthBearer(),
    openapi_extra={
        'responses': {
            409: {
                'description': 'A pronúncia para o termo já existe.',
                'content': {
                    'application/json': {
                        'example': {'detail': 'pronunciation already exists.'}
                    }
                },
            },
        }
    },
)
@permission_required([is_admin])
def create_pronunciation(request, pronunciation_schema: schema.TermPronunciationSchema):
    try:
        return 201, TermPronunciation.objects.create(
            **pronunciation_schema.model_dump(exclude_none=True)
        )
    except IntegrityError:
        raise HttpError(status_code=409, message='pronunciation already exists.')


@pronunciation_router.get(
    path='',
    response={200: schema.TermPronunciationView, 404: core_schema.NotFound},
    summary='Consulta das pronúncias.',
    description='Endpoint utilizado para consultar pronúncias com áudio, fonemas e descrição sobre um determinado modelo.',
)
def get_pronunciation(
    request,
    pronunciation_schema: Query[schema.TermPronunciationLinkSchema],
):
    return get_object_or_404(
        TermPronunciation, pronunciation_schema.get_filter_expression()
    )
