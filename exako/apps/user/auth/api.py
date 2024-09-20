from ninja import Form, Router

from exako.apps.core.schema import NotAuthenticated
from exako.apps.user.auth.exception import InvalidToken
from exako.apps.user.auth.schema import Token
from exako.apps.user.auth.token import AuthBearer, create_jwt_access_token
from exako.apps.user.models import User

auth_router = Router()


@auth_router.post(
    '/token',
    tags=['auth'],
    summary='Token de autenticação',
    description='Endpoint para pegar o token de autenticação do usuário.',
    response={
        200: Token,
        401: NotAuthenticated,
    },
)
def create_access_token(request, email: str = Form(...), password: str = Form(...)):
    user = User.objects.filter(email=email).first()
    if user is None:
        raise InvalidToken

    if not user.check_password(password):
        raise InvalidToken

    return {
        'access_token': create_jwt_access_token(user),
        'token_type': 'Bearer',
    }


@auth_router.post(
    'token/refresh',
    tags=['auth'],
    summary='Atualizar token de autenticação',
    description='Endpoint para atualizar o token de autenticação do usuário.',
    response={
        200: Token,
        401: NotAuthenticated,
    },
    auth=AuthBearer(),
)
def refresh_access_token(request):
    if not request.user:
        return InvalidToken

    return {
        'access_token': create_jwt_access_token(request.user),
        'token_type': 'Bearer',
    }
