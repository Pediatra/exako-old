from ninja import Schema


class NotAuthenticated(Schema):
    detail: str = 'could not validate credentials.'


class NotFound(Schema):
    detail: str = 'object not found.'


class PermissionDenied(Schema):
    detail: str = 'not enough permissions.'
