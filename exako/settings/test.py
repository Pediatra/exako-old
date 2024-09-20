from ._base import *

DEBUG = False

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

DATABASES['default'] = {**DATABASES['default'], 'NAME': 'exako_test'}
