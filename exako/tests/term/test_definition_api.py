import pytest
from django.urls import reverse_lazy

from exako.apps.core.query import set_url_params
from exako.apps.term.api.schema import TermDefinitionTranslationView, TermDefinitionView
from exako.apps.term.constants import Language, Level, PartOfSpeech
from exako.apps.term.models import TermDefinition, TermDefinitionTranslation
from exako.tests.factories.term import (
    TermDefinitionFactory,
    TermDefinitionTranslationFactory,
    TermFactory,
    TermLexicalFactory,
)

pytestmark = pytest.mark.django_db


create_term_definition_route = reverse_lazy('api-1.0.0:create_definition')
create_term_definition_translation_route = reverse_lazy(
    'api-1.0.0:create_definition_translation'
)


def list_term_definition_route(
    term=None,
    language=None,
    part_of_speech=None,
    level=None,
    term_lexical=None,
):
    url = str(reverse_lazy('api-1.0.0:list_definition'))
    return set_url_params(
        url,
        term=term,
        language=language,
        part_of_speech=part_of_speech,
        level=level,
        term_lexical=term_lexical,
    )


def get_term_definition_translation_route(term_definition, language):
    return reverse_lazy(
        'api-1.0.0:get_definition_translation',
        kwargs={'term_definition': term_definition, 'language': language},
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition(client, generate_payload, token_header):
    term = TermFactory()
    payload = generate_payload(TermDefinitionFactory, term=term)

    response = client.post(
        create_term_definition_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    assert TermDefinitionView(**response.json()) == TermDefinitionView.from_orm(
        TermDefinition.objects.get(id=response.json()['id'])
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_with_lexical_id(client, generate_payload, token_header):
    term = TermFactory()
    term_lexical = TermLexicalFactory(term=term)
    payload = generate_payload(
        TermDefinitionFactory,
        part_of_speech=PartOfSpeech.LEXICAL,
        term=term,
        term_lexical=term_lexical,
    )

    response = client.post(
        create_term_definition_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    definition = TermDefinition.objects.get(id=response.json()['id'])
    assert definition.term_lexical.id == term_lexical.id


def test_create_term_definition_user_is_not_authenticated(client, generate_payload):
    term = TermFactory()
    payload = generate_payload(TermDefinitionFactory, term=term)

    response = client.post(
        create_term_definition_route,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_term_definition_user_not_enough_permission(
    client, generate_payload, token_header
):
    term = TermFactory()
    payload = generate_payload(TermDefinitionFactory, term=term)

    response = client.post(
        create_term_definition_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 403


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_term_not_found(client, generate_payload, token_header):
    payload = generate_payload(TermDefinitionFactory)
    payload.update(term=1257)

    response = client.post(
        create_term_definition_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 404


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_conflict(client, generate_payload, token_header):
    term = TermFactory()
    payload = generate_payload(TermDefinitionFactory, term=term)
    TermDefinitionFactory(**payload)

    response = client.post(
        create_term_definition_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 409


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_term_lexical_invalid_language_ref(
    client, generate_payload, token_header
):
    term = TermFactory(language=Language.CHINESE)
    term_lexical = TermLexicalFactory(term__language=Language.PORTUGUESE_BRASILIAN)
    payload = generate_payload(
        TermDefinitionFactory,
        term=term,
        term_lexical=term_lexical,
    )

    response = client.post(
        create_term_definition_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'term_lexical language have to be the same as term reference.'
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_translation(client, generate_payload, token_header):
    term_definition = TermDefinitionFactory()
    payload = generate_payload(
        TermDefinitionTranslationFactory,
        term_definition=term_definition,
    )

    response = client.post(
        create_term_definition_translation_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    assert TermDefinitionTranslationView(
        **response.json()
    ) == TermDefinitionTranslationView.from_orm(
        TermDefinitionTranslation.objects.get(
            term_definition=term_definition.id,
            language=payload['language'],
        )
    )


def test_create_term_definition_translation_user_is_not_authenticated(
    client, generate_payload
):
    term_definition = TermDefinitionFactory()
    payload = generate_payload(
        TermDefinitionTranslationFactory, term_definition=term_definition
    )

    response = client.post(
        create_term_definition_translation_route,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_term_definition_translation_user_not_enough_permission(
    client, generate_payload, token_header
):
    term_definition = TermDefinitionFactory()
    payload = generate_payload(
        TermDefinitionTranslationFactory, term_definition=term_definition
    )

    response = client.post(
        create_term_definition_translation_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 403


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_translation_definition_does_not_exists(
    client, generate_payload, token_header
):
    payload = generate_payload(TermDefinitionTranslationFactory)
    payload.update(term_definition=51892)

    response = client.post(
        create_term_definition_translation_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 404


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_translation_conflict(
    client, generate_payload, token_header
):
    term_definition = TermDefinitionFactory()
    payload = generate_payload(
        TermDefinitionTranslationFactory, term_definition=term_definition
    )
    TermDefinitionTranslationFactory(**payload)

    response = client.post(
        create_term_definition_translation_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 409


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_translation_same_language_reference(
    client, generate_payload, token_header
):
    term_definition = TermDefinitionFactory(
        term__language=Language.CHINESE,
        term_lexical=None,
    )
    payload = generate_payload(
        TermDefinitionTranslationFactory,
        term_definition=term_definition,
        language=Language.CHINESE,
    )

    response = client.post(
        create_term_definition_translation_route,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'translation language reference cannot be same as language.'
    )


def test_list_term_definition(client):
    term = TermFactory()
    definitions = TermDefinitionFactory.create_batch(term=term, size=5)
    TermDefinitionFactory.create_batch(size=5)

    response = client.get(list_term_definition_route(term=term.id))

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert [TermDefinitionView(**definition) for definition in response.json()] == [
        TermDefinitionView.from_orm(definition) for definition in definitions
    ]


def test_list_term_definition_empty(client):
    term = TermFactory()
    TermDefinitionFactory.create_batch(size=5)

    response = client.get(list_term_definition_route(term=term.id))

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_list_term_definition_filter_part_of_speech(client):
    term = TermFactory()
    definitions = TermDefinitionFactory.create_batch(
        term=term,
        size=5,
        part_of_speech=PartOfSpeech.ADJECTIVE,
    )
    TermDefinitionFactory.create_batch(
        term=term,
        size=5,
        part_of_speech=PartOfSpeech.VERB,
    )

    response = client.get(
        list_term_definition_route(
            term=term.id,
            part_of_speech=PartOfSpeech.ADJECTIVE,
        )
    )

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert [TermDefinitionView(**definition) for definition in response.json()] == [
        TermDefinitionView.from_orm(definition) for definition in definitions
    ]


def test_list_term_definition_filter_level(client):
    term = TermFactory()
    definitions = TermDefinitionFactory.create_batch(
        term=term,
        size=5,
        level=Level.ADVANCED,
    )
    TermDefinitionFactory.create_batch(
        term=term,
        size=5,
        level=Level.BEGINNER,
    )

    response = client.get(
        list_term_definition_route(
            term=term.id,
            level=Level.ADVANCED,
        )
    )

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert [TermDefinitionView(**definition) for definition in response.json()] == [
        TermDefinitionView.from_orm(definition) for definition in definitions
    ]


def test_list_term_definition_filter_term_lexical(client):
    term = TermFactory()
    lexical = TermLexicalFactory()
    definitions = TermDefinitionFactory.create_batch(
        term=term,
        term_lexical=lexical,
        size=5,
    )
    TermDefinitionFactory.create_batch(term=term, size=5)

    response = client.get(
        list_term_definition_route(
            term=term.id,
            term_lexical=lexical.id,
        )
    )

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert [TermDefinitionView(**definition) for definition in response.json()] == [
        TermDefinitionView.from_orm(definition) for definition in definitions
    ]


def test_get_term_definition_translation(client):
    translation = TermDefinitionTranslationFactory()

    response = client.get(
        get_term_definition_translation_route(
            term_definition=translation.term_definition.id,
            language=translation.language,
        )
    )

    assert response.status_code == 200
    assert TermDefinitionTranslationView(
        **response.json()
    ) == TermDefinitionTranslationView.from_orm(translation)


def test_get_term_definition_translation_not_found(client):
    TermDefinitionTranslationFactory()

    response = client.get(
        get_term_definition_translation_route(
            term_definition=123,
            language=Language.PORTUGUESE_BRASILIAN,
        )
    )

    assert response.status_code == 404
