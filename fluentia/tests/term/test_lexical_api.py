import pytest
from django.urls import reverse_lazy

from fluentia.apps.core.query import set_url_params
from fluentia.apps.term.api.schema import TermLexicalView
from fluentia.apps.term.constants import TermLexicalType
from fluentia.apps.term.models import TermLexical
from fluentia.tests.factories.term import TermFactory, TermLexicalFactory

pytestmark = pytest.mark.django_db


create_term_lexical_route = reverse_lazy('api-1.0.0:create_lexical')


def list_term_lexical_route(term=None, type=None):
    url = str(reverse_lazy('api-1.0.0:list_lexical'))
    return set_url_params(
        url,
        term=term,
        type=type,
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_lexical(client, generate_payload, token_header):
    term = TermFactory()
    payload = generate_payload(TermLexicalFactory, term=term)

    response = client.post(
        create_term_lexical_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    assert TermLexicalView(**response.json()) == TermLexicalView(
        id=response.json()['id'], **payload
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_lexical_with_term_value_ref(
    client, generate_payload, token_header
):
    term = TermFactory()
    term_ref = TermFactory()
    payload = generate_payload(
        TermLexicalFactory,
        term=term,
        value=None,
        term_value_ref=term_ref,
    )

    response = client.post(
        create_term_lexical_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    term_lexical = TermLexical.objects.get(id=response.json()['id'])
    assert term_lexical.term_value_ref == term_ref


def test_create_term_lexical_user_is_not_authenticated(client, generate_payload):
    term = TermFactory()
    payload = generate_payload(TermLexicalFactory, term=term)

    response = client.post(
        create_term_lexical_route,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_term_lexical_user_does_not_have_permission(
    client, generate_payload, token_header
):
    term = TermFactory()
    payload = generate_payload(TermLexicalFactory, term=term)

    response = client.post(
        create_term_lexical_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 403


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_lexical_term_does_not_exists(
    client, generate_payload, token_header
):
    payload = generate_payload(TermLexicalFactory)
    payload.update(term=1256)

    response = client.post(
        create_term_lexical_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 404


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_lexical_conflict(client, generate_payload, token_header):
    term = TermFactory()
    payload = generate_payload(TermLexicalFactory, term=term)
    TermLexicalFactory(**payload)

    response = client.post(
        create_term_lexical_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 409


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_lexical_conflict_term_value_ref(
    client, generate_payload, token_header
):
    term = TermFactory()
    term_value_ref = TermFactory()
    payload = generate_payload(
        TermLexicalFactory,
        term=term,
        value=None,
        term_value_ref=term_value_ref,
    )
    TermLexicalFactory(**payload)

    response = client.post(
        create_term_lexical_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 409


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_lexical_value_ref_same_as_term(
    client, generate_payload, token_header
):
    term = TermFactory()
    payload = generate_payload(
        TermLexicalFactory,
        term=term,
        value=None,
        term_value_ref=term,
    )

    response = client.post(
        create_term_lexical_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'term_value_ref cannot be the same as term lexical reference.'
        in response.json()['detail']
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_lexical_without_value(client, generate_payload, token_header):
    term = TermFactory()
    payload = generate_payload(
        TermLexicalFactory,
        term=term,
        term_value_ref=None,
        value=None,
    )

    response = client.post(
        create_term_lexical_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'you need to provied at least one value ref.'
        in response.json()['detail'][0]['msg']
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_lexical_both_value(client, generate_payload, token_header):
    term = TermFactory()
    payload = generate_payload(
        TermLexicalFactory,
        term=term,
        term_value_ref=TermFactory(),
    )

    response = client.post(
        create_term_lexical_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'you cannot reference two values at once (value, term_value_ref).'
        in response.json()['detail'][0]['msg']
    )


def test_list_term_lexical(client):
    term = TermFactory()
    lexicals = TermLexicalFactory.create_batch(
        term=term,
        size=5,
    )

    response = client.get(
        list_term_lexical_route(
            term=term.id,
        )
    )

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert [TermLexicalView(**lexical) for lexical in response.json()] == [
        TermLexicalView.from_orm(lexical) for lexical in lexicals
    ]


def test_list_term_lexical_filter_type(client):
    term = TermFactory()
    lexicals = TermLexicalFactory.create_batch(
        term=term,
        type=TermLexicalType.ANTONYM,
        size=5,
    )

    response = client.get(
        list_term_lexical_route(
            term=term.id,
            type=TermLexicalType.ANTONYM,
        )
    )

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert [TermLexicalView(**lexical) for lexical in response.json()] == [
        TermLexicalView.from_orm(lexical) for lexical in lexicals
    ]


def test_list_term_lexical_empty(client):
    term = TermFactory()
    TermLexicalFactory.create_batch(
        term=term,
        type=TermLexicalType.INFLECTION,
        size=5,
    )

    response = client.get(
        list_term_lexical_route(
            term=term.id,
            type=TermLexicalType.ANTONYM,
        )
    )

    assert response.status_code == 200
    assert len(response.json()) == 0
