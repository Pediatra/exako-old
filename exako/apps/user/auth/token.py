from typing import Any, Optional

from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone
from jose import JWTError, jwt
from ninja.security import HttpBearer

from exako.apps.user.auth.exception import InvalidToken
from exako.apps.user.models import User


def create_jwt_access_token(user) -> str:
    data = {
        'sub': user.email,
        'name': user.name,
        'iat': timezone.now(),
        'exp': timezone.now() + settings.TOKEN_EXPIRATION_DELTA,
    }

    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return token


class AuthBearer(HttpBearer):
    def __call__(self, request: HttpRequest) -> Optional[Any]:
        token = super().__call__(request)
        if token is None:
            raise InvalidToken
        return token

    def authenticate(self, request, token):
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={'require_sub': True},
            )
            email: str = payload.get('sub')
        except JWTError:
            raise InvalidToken

        user = User.objects.filter(email=email).first()
        if user is None:
            raise InvalidToken

        setattr(request, 'user', user)
        setattr(request, 'is_authenticated', True)
        return token
