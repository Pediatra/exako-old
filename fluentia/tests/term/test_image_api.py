import json

import pytest
from django.urls import reverse_lazy

from fluentia.tests.factories.term import TermFactory, TermImageFactory

pytestmark = pytest.mark.django_db

create_term_image_router = reverse_lazy('api-1.0.0:create_term_image')


def get_term_image_router(term_id):
    return reverse_lazy('api-1.0.0:get_term_image', kwargs={'term_id': term_id})


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_image(client, token_header):
    term_image = TermImageFactory()
    term = TermFactory()
    response = client.post(
        create_term_image_router,
        data={
            'exercise_schema': json.dumps({'term': term.id}),
            'image': term_image.image,
        },
        headers=token_header,
    )

    assert response.status_code == 201
    assert response.json()['image'] is not None


def test_create_term_image_not_authenticated(client):
    response = client.post(
        create_term_image_router,
        data={
            'exercise_schema': json.dumps({'term': TermFactory().id}),
            'image': TermImageFactory().image,
        },
    )

    assert response.status_code == 401


def test_create_term_image_not_enough_permission(client, token_header):
    response = client.post(
        create_term_image_router,
        data={
            'exercise_schema': json.dumps({'term': TermFactory().id}),
            'image': TermImageFactory().image,
        },
        headers=token_header,
    )

    assert response.status_code == 403


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_image_not_found(client, token_header):
    response = client.post(
        create_term_image_router,
        data={
            'exercise_schema': json.dumps({'term': 41256}),
            'image': TermImageFactory().image,
        },
        headers=token_header,
    )

    assert response.status_code == 404


def test_get_term_image(client):
    term_image = TermImageFactory()

    response = client.get(get_term_image_router(term_image.term.id))

    assert response.status_code == 200
    assert response.json()['image'] is not None


def test_get_term_image_not_found(client):
    response = client.get(get_term_image_router(14580))

    assert response.status_code == 404
