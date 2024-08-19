import pytest
from django.contrib.auth.hashers import make_password
from django.forms.models import model_to_dict
from django.test import Client
from django.urls import reverse_lazy

from fluentia.tests.factories.user import UserFactory


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
        data={'email': user.email, 'password': user.clean_password},
    )
    return {'Authorization': f'Bearer {response.json()["access_token"]}'}


@pytest.fixture
def generate_payload():
    def _generate(factory, exclude=None, include=None, **kwargs):
        result = factory.build(**kwargs)
        model_dict = model_to_dict(result, fields=include, exclude=exclude)
        return {k: v for k, v in model_dict.items() if v is not None}

    return _generate
