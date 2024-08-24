import pytest
from django.urls import reverse_lazy

from fluentia.apps.core.query import set_url_params
from fluentia.apps.term.api.schema import TermPronunciationView
from fluentia.apps.term.constants import TermLexicalType
from fluentia.tests.factories.term import (
    TermExampleFactory,
    TermFactory,
    TermLexicalFactory,
    TermPronunciationFactory,
)

pytestmark = pytest.mark.django_db


create_pronunciation_route = reverse_lazy('api-1.0.0:create_pronunciation')


def get_pronunciation_route(
    term=None,
    term_example=None,
    term_lexical=None,
):
    url = str(reverse_lazy('api-1.0.0:get_pronunciation'))
    return set_url_params(
        url,
        term=term,
        term_example=term_example,
        term_lexical=term_lexical,
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_pronunciation(client, generate_payload, token_header):
    term = TermFactory()
    payload = generate_payload(TermPronunciationFactory, term=term)

    response = client.post(
        create_pronunciation_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    assert TermPronunciationView(**response.json()) == TermPronunciationView(
        id=response.json()['id'], **payload
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_pronunciation_example(client, generate_payload, token_header):
    term_example = TermExampleFactory()
    payload = generate_payload(TermPronunciationFactory, term_example=term_example)

    response = client.post(
        create_pronunciation_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    assert TermPronunciationView(**response.json()) == TermPronunciationView(
        id=response.json()['id'], **payload
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_pronunciation_lexical(client, generate_payload, token_header):
    term_lexical = TermLexicalFactory(type=TermLexicalType.FORM)
    payload = generate_payload(TermPronunciationFactory, term_lexical=term_lexical)

    response = client.post(
        create_pronunciation_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    assert TermPronunciationView(**response.json()) == TermPronunciationView(
        id=response.json()['id'], **payload
    )


def test_create_term_pronunciation_user_is_not_authenticated(client, generate_payload):
    payload = generate_payload(TermPronunciationFactory)

    response = client.post(create_pronunciation_route, json=payload)

    assert response.status_code == 401


def test_create_term_pronunciation_user_not_enough_permission(
    client, generate_payload, token_header
):
    term = TermFactory()
    payload = generate_payload(TermPronunciationFactory, term=term)

    response = client.post(
        create_pronunciation_route,
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 403


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@pytest.mark.parametrize(
    'model',
    [
        {'term': 12515},
        {'term_example': 1241245},
        {'term_lexical': 1515},
    ],
)
def test_create_term_pronunciation_model_link_not_found(
    client, generate_payload, token_header, model
):
    payload = generate_payload(TermPronunciationFactory)
    payload.update(**model)

    response = client.post(
        create_pronunciation_route,
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 404


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_pronunciation_already_exists(
    client, generate_payload, token_header
):
    term = TermFactory()
    payload = generate_payload(TermPronunciationFactory, term=term)
    TermPronunciationFactory(**payload)

    response = client.post(
        create_pronunciation_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 409


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_pronunciation_model_link_attribute_not_set(
    client, generate_payload, token_header
):
    payload = generate_payload(TermPronunciationFactory, term=None)

    response = client.post(
        create_pronunciation_route,
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 422
    assert 'at least one object to link' in response.json()['detail'][0]['msg']


@pytest.mark.parametrize(
    'link_attr',
    [
        {
            'term_example': 123,
            'term': 616,
        },
        {
            'term_example': 123,
            'term_lexical': 400,
        },
    ],
)
@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_pronunciation_multiple_models(
    client, generate_payload, token_header, link_attr
):
    payload = generate_payload(TermPronunciationFactory)
    payload.update(link_attr)

    response = client.post(
        create_pronunciation_route,
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 422
    assert 'you can reference only one object.' in response.json()['detail'][0]['msg']


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_pronunciation_lexical_with_term_value_ref(
    client, generate_payload, token_header
):
    term_value_ref = TermFactory()
    term_lexical = TermLexicalFactory(term_value_ref=term_value_ref)
    payload = generate_payload(TermPronunciationFactory, term_lexical=term_lexical)

    response = client.post(
        create_pronunciation_route,
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 422
    assert (
        'lexical with term_value_ref cannot have a pronunciation.'
        in response.json()['detail']
    )


def test_get_term_pronunciation(client):
    term = TermFactory()
    pronunciation = TermPronunciationFactory(term=term)
    TermPronunciationFactory.create_batch(5)

    response = client.get(get_pronunciation_route(term=term.id))

    assert response.status_code == 200
    assert TermPronunciationView(**response.json()) == TermPronunciationView.from_orm(
        pronunciation
    )


def test_get_term_pronunciation_example(client):
    term_example = TermExampleFactory()
    pronunciation = TermPronunciationFactory(term_example=term_example)
    TermPronunciationFactory.create_batch(5)

    response = client.get(
        get_pronunciation_route(
            term_example=term_example.id,
        )
    )

    assert response.status_code == 200
    assert TermPronunciationView(**response.json()) == TermPronunciationView.from_orm(
        pronunciation
    )


def test_get_term_pronunciation_lexical(client):
    term_lexical = TermLexicalFactory(type=TermLexicalType.FORM)
    pronunciation = TermPronunciationFactory(term_lexical=term_lexical)
    TermPronunciationFactory.create_batch(5)

    response = client.get(
        get_pronunciation_route(
            term_lexical=term_lexical.id,
        )
    )

    assert response.status_code == 200
    assert TermPronunciationView(**response.json()) == TermPronunciationView.from_orm(
        pronunciation
    )


def test_get_term_pronunciation_not_found(client):
    term = TermFactory()
    TermPronunciationFactory.create_batch(5)

    response = client.get(get_pronunciation_route(term=term.id))

    assert response.status_code == 404


def test_get_term_pronunciation_model_not_set(client):
    response = client.get(get_pronunciation_route())

    assert response.status_code == 422


def test_get_term_pronunciation_model_multiple_invalid(client):
    response = client.get(
        get_pronunciation_route(
            term=15256,
            term_example=612,
        )
    )

    assert response.status_code == 422


def test_get_term_pronunciation_multiple_models(client):
    response = client.get(
        get_pronunciation_route(
            term_example=12451,
            term_lexical=61612,
        )
    )

    assert response.status_code == 422
