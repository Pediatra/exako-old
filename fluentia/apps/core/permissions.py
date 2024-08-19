from functools import wraps

from ninja.errors import HttpError


def permission_required(permissions):
    def wrapper(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            for permission in permissions:
                permission(request, *args, **kwargs, endpoint=func)
            return func(request, *args, **kwargs)

        return inner

    return wrapper


def is_admin(request, *args, **kwargs):
    if not request.user.is_superuser:
        raise HttpError(status_code=403, message='not enough permission.')
