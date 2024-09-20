import os
import shutil
from itertools import chain

import pytest
from django.contrib.auth.hashers import make_password
from django.db.models import ForeignKey, ManyToManyField, OneToOneField
from django.test import Client
from django.urls import reverse_lazy

from exako.tests.factories.user import UserFactory


@pytest.fixture
def client():
    yield Client()


@pytest.fixture
def user(request):
    param = getattr(request, 'param', {})
    password = param.pop('password', 'pass123')

    user = UserFactory(password=make_password(password), **param)
    user.__dict__['clean_password'] = password

    return user


@pytest.fixture
def token_header(client, user):
    url = reverse_lazy('api-1.0.0:create_access_token')
    response = client.post(
        url,
        data={
            'email': user.email,
            'password': user.clean_password,
        },
    )
    return {'Authorization': f'Bearer {response.json()["access_token"]}'}


@pytest.fixture
def generate_payload():
    def model_to_dict(instance, fields=None, exclude=None):
        opts = instance._meta
        data = {}
        for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
            if not getattr(f, 'editable', False):
                continue
            if fields is not None and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue

            if isinstance(f, (ForeignKey, OneToOneField)):
                related_instance = getattr(instance, f.name)
                if related_instance is not None:
                    data[f.name] = related_instance.pk
                else:
                    data[f.name] = None

            elif isinstance(f, ManyToManyField):
                data[f.name] = list(
                    getattr(instance, f.name).values_list('pk', flat=True)
                )
            else:
                data[f.name] = f.value_from_object(instance)

        return data

    def _generate(factory, exclude=None, include=None, **kwargs):
        result = factory.build(**kwargs)
        model_dict = model_to_dict(result, fields=include, exclude=exclude)
        return {k: v for k, v in model_dict.items() if v is not None}

    return _generate


@pytest.fixture(autouse=True)
def override_media_path(settings):
    settings.MEDIA_ROOT = settings.BASE_DIR / 'media_test'


@pytest.fixture(autouse=True)
def delete_term_media_dir(settings):
    yield
    if os.path.exists(settings.MEDIA_ROOT / 'term'):
        shutil.rmtree(settings.MEDIA_ROOT / 'term')
