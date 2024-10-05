from django.db.models import Q
from ninja import Query, Router
from ninja.errors import HttpError

from exako.apps.core import schema as core_schema
from exako.apps.core.permissions import is_admin, permission_required
from exako.apps.term.api import schema
from exako.apps.term.models import TermLexical
from exako.apps.user.auth.token import AuthBearer

lexical_router = Router()


@lexical_router.post(
    path='',
    response={
        201: schema.TermLexicalView,
        401: core_schema.NotAuthenticated,
        403: core_schema.PermissionDenied,
        404: core_schema.NotFound,
    },
    summary='Criação de relação de uma relação lexical.',
    description='Endpoint utilizado para criação de relações lexicais entre termos, sendo elas sinônimos, antônimos e conjugações.',
    auth=AuthBearer(),
    openapi_extra={
        'responses': {
            409: {
                'description': 'O léxico já existe para esse termo.',
                'content': {
                    'application/json': {
                        'example': {'detail': 'lexical already exists to this term.'}
                    }
                },
            },
        }
    },
)
@permission_required([is_admin])
def create_lexical(
    request,
    lexical_schema: schema.TermLexicalSchema,
):
    if TermLexical.objects.filter(
        Q(
            value__ct=lexical_schema.value,
            term_id=lexical_schema.term,
            type=lexical_schema.type,
        )
        | Q(
            term_value_ref_id=lexical_schema.term_value_ref,
            term_id=lexical_schema.term,
            type=lexical_schema.type,
        )
    ).exists():
        raise HttpError(status_code=409, message='lexical already exists to this term.')
    return 201, TermLexical.objects.create(**lexical_schema.model_dump())


@lexical_router.get(
    path='/lexical',
    response={200: list[schema.TermLexicalView]},
    summary='Consulta de relação de uma relação lexical.',
    description='Endpoint utilizado para consultar de relações lexicais entre termos, sendo elas sinônimos, antônimos e conjugações.',
)
def list_lexical(request, filter_schema: schema.TermLexicalFilter = Query()):
    return TermLexical.objects.filter(filter_schema.get_filter_expression())
