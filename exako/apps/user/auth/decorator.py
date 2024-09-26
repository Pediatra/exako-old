from functools import wraps

from django.conf import settings
from django.http import HttpResponse

from exako.apps.user.auth.exception import InvalidToken
from exako.apps.user.auth.token import AuthBearer


def login_required(func=None, auth=AuthBearer()):
    def decorator(f):
        @wraps(f)
        def wrapper(request, *args, **kwargs):
            try:
                auth(request)
            except InvalidToken:
                response = HttpResponse()
                response.status_code = 302
                response.headers['HX-Redirect'] = settings.LOGIN_URL
                return response
            return f(request, *args, **kwargs)

        return wrapper

    if func:
        return decorator(func)
    return decorator
