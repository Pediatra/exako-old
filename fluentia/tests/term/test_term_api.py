import pytest
from django.urls import reverse_lazy

from fluentia.apps.core.query import set_url_params
from fluentia.apps.term.api.schema import TermView
from fluentia.apps.term.constants import Language, TermLexicalType
from fluentia.tests.factories.term import (
    TermDefinitionTranslationFactory,
    TermFactory,
    TermLexicalFactory,
)

pytestmark = pytest.mark.django_db


create_term_route = reverse_lazy('api-1.0.0:create_term')


def get_term_route(expression, origin_language):
    url = str(reverse_lazy('api-1.0.0:get_term'))
    return set_url_params(
        url,
        expression=expression,
        origin_language=origin_language,
    )


def get_term_id_route(id):
    return reverse_lazy('api-1.0.0:get_term_id', kwargs={'term_id': id})


def search_term_route(expression, origin_language):
    url = str(reverse_lazy('api-1.0.0:search_term'))
    return set_url_params(
        url,
        expression=expression,
        origin_language=origin_language,
    )


def search_meaning_route(expression, origin_language, translation_language):
    url = str(reverse_lazy('api-1.0.0:search_meaning'))
    return set_url_params(
        url,
        expression=expression,
        origin_language=origin_language,
        translation_language=translation_language,
    )


def term_index_route(char, origin_language):
    url = str(reverse_lazy('api-1.0.0:term_index'))
    return set_url_params(
        url,
        char=char,
        origin_language=origin_language,
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term(client, generate_payload, token_header):
    payload = generate_payload(TermFactory)

    response = client.post(
        create_term_route,
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 201
    assert TermView(**response.json()) == TermView(id=response.json()['id'], **payload)


def test_create_term_not_authenticated(client, generate_payload):
    payload = generate_payload(TermFactory)

    response = client.post(
        create_term_route,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_term_not_enough_permission(client, generate_payload, token_header):
    payload = generate_payload(TermFactory)

    response = client.post(
        create_term_route,
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 403


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_already_exists(client, generate_payload, token_header):
    payload = generate_payload(TermFactory)
    TermFactory(**payload)

    response = client.post(
        create_term_route,
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 409


def test_get_term(client):
    term = TermFactory(expression='ãQübérmäßíg âçãoQã')

    response = client.get(get_term_route('aqubermassig acaoqa', term.origin_language))

    assert response.status_code == 200
    assert TermView(**response.json()) == TermView.from_orm(term)


def test_get_term_lexical(client):
    term = TermFactory()
    TermLexicalFactory(
        term=term,
        type=TermLexicalType.INFLECTION,
        value='ãQübérmäßíg âçãoQã',
    )

    response = client.get(get_term_route('aqubermassig acaoqa', term.origin_language))

    assert response.status_code == 200
    assert TermView(**response.json()) == TermView.from_orm(term)


def test_get_term_not_found(client):
    response = client.get(get_term_route('expression', Language.PORTUGUESE))

    assert response.status_code == 404


def test_get_term_id(client):
    term = TermFactory()

    response = client.get(get_term_id_route(term.id))

    assert response.status_code == 200
    assert TermView(**response.json()) == TermView.from_orm(term)


def test_get_term_id_not_found(client):
    response = client.get(get_term_id_route(124780))

    assert response.status_code == 404


def test_search_term(client):
    term = TermFactory(expression='ãQübérmäßíg âçãoQã')
    TermFactory.create_batch(size=5)

    response = client.get(search_term_route('aqubermassi acaoq', term.origin_language))

    assert response.status_code == 200
    assert len(response.json()['items']) == 1
    assert TermView.from_orm(term) in [
        TermView(**res) for res in response.json()['items']
    ]


def test_search_term_lexical(client):
    term = TermFactory()
    TermLexicalFactory(
        term=term,
        type=TermLexicalType.INFLECTION,
        value='ãQübérmäßíg âçãoQã',
    )
    TermFactory.create_batch(size=5)

    response = client.get(search_term_route('aqubermassi acaoq', term.origin_language))

    assert response.status_code == 200
    assert len(response.json()['items']) == 1
    assert TermView.from_orm(term) in [
        TermView(**res) for res in response.json()['items']
    ]


def test_search_term_empty(client):
    TermFactory.create_batch(size=5)

    response = client.get(search_term_route('aqubermassi acaoq', Language.PORTUGUESE))

    assert response.status_code == 200
    assert len(response.json()['items']) == 0


def test_search_meaning(client):
    term_definition_translation = TermDefinitionTranslationFactory(
        meaning='ãQübérmäßíg âçãoQã'
    )

    response = client.get(
        search_meaning_route(
            'aqubermassi acaoq',
            term_definition_translation.term_definition.term.origin_language,
            term_definition_translation.language,
        )
    )

    assert response.status_code == 200
    assert len(response.json()['items']) == 1
    assert TermView.from_orm(term_definition_translation.term_definition.term) in [
        TermView(**res) for res in response.json()['items']
    ]


def test_search_meaning_empty(client):
    TermFactory.create_batch(size=5)

    response = client.get(
        search_meaning_route(
            'aqubermassi acaoq',
            Language.PORTUGUESE,
            Language.ENGLISH,
        )
    )

    assert response.status_code == 200
    assert len(response.json()['items']) == 0


def test_term_index(client):
    terms = [
        TermFactory(expression=f'a - {n}', origin_language=Language.PORTUGUESE)
        for n in range(5)
    ]

    response = client.get(term_index_route('A', Language.PORTUGUESE))

    assert response.status_code == 200
    assert [TermView.from_orm(term) for term in terms] == [
        TermView(**res) for res in response.json()['items']
    ]
