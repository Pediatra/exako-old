from datetime import datetime

from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone
from jose import jwt
from pytest import mark, raises

from exako.apps.user.auth.exception import InvalidToken
from exako.apps.user.auth.token import AuthBearer, create_jwt_access_token
from exako.tests.factories.user import UserFactory

pytestmark = mark.django_db


def test_create_jwt_token_access():
    user = UserFactory()

    token = create_jwt_access_token(user)

    decoded_token = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={'require_sub': True},
    )

    assert decoded_token.get('sub') == user.email
    assert decoded_token.get('name') == user.name


def test_auth_bearer_token_authentication():
    auth = AuthBearer()
    request = HttpRequest()

    user = UserFactory()
    token = create_jwt_access_token(user)

    valid_token = auth.authenticate(request, token)

    assert valid_token == token
    assert request.user == user


def test_auth_bearer_token_authentication_with_invalid_credentials():
    auth = AuthBearer()
    request = HttpRequest()

    with raises(InvalidToken):
        auth.authenticate(request, 'token')


def test_auth_bearer_token_authentication_with_invalid_user():
    auth = AuthBearer()
    request = HttpRequest()

    data = {
        'sub': 'fake@gmail.com',
        'name': 'test',
        'iat': datetime.utcnow(),
        'exp': timezone.now() + settings.TOKEN_EXPIRATION_DELTA,
    }
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    with raises(InvalidToken):
        auth.authenticate(request, token)
