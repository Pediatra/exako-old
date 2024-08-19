from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from jose import JWTError, jwt
from ninja.security import HttpBearer

from fluentia.apps.user.auth.exception import InvalidToken
from fluentia.apps.user.models import User

TOKEN_EXPIRATION_DELTA = timedelta(days=7)
ALGORITHM = 'HS256'


def create_jwt_access_token(user: User) -> str:
    data = {
        'sub': user.email,
        'name': user.name,
        'iat': datetime.utcnow(),
        'exp': timezone.now() + TOKEN_EXPIRATION_DELTA,
    }

    return jwt.encode(data, settings.SECRET_KEY, algorithm=ALGORITHM)


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[ALGORITHM],
                options={'require_sub': True},
            )
            email: str = payload.get('sub')
        except JWTError:
            raise InvalidToken

        user = User.objects.filter(email=email).first()
        if user is None:
            raise InvalidToken

        setattr(request, 'user', user)
        return token
