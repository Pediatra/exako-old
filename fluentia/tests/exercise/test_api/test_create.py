import pytest
from django.urls import reverse_lazy

from fluentia.apps.exercise.api.schema import ExerciseSchemaView
from fluentia.apps.exercise.models import Exercise, ExerciseLevel
from fluentia.apps.term.constants import Level
from fluentia.tests.factories import exercise as exercise_factory
from fluentia.tests.factories.term import (
    TermDefinitionFactory,
    TermExampleFactory,
    TermFactory,
)

pytestmark = pytest.mark.django_db


create_exercise_router = reverse_lazy('api-1.0.0:create_exercise')

parametrize_exercies = pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factory.OrderSentenceFactory,
        exercise_factory.ListenTermFactory,
        exercise_factory.ListenTermLexicalFactory,
        exercise_factory.ListenSentenceFactory,
        exercise_factory.ListenTermMChoiceFactory,
        exercise_factory.SpeakTermFactory,
        exercise_factory.SpeakTermLexicalFactory,
        exercise_factory.SpeakSentenceFactory,
        exercise_factory.TermMChoiceFactory,
        exercise_factory.TermLexicalMChoiceFactory,
        exercise_factory.TermDefinitionMChoiceFactory,
        exercise_factory.TermImageMChoiceFactory,
        exercise_factory.TermImageMChoiceTextFactory,
        exercise_factory.TermConnectionFactory,
    ],
)


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@parametrize_exercies
def test_create_exercise(client, generate_payload, token_header, exercise_factory):
    payload = generate_payload(exercise_factory)

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    assert ExerciseSchemaView(**response.json()) == ExerciseSchemaView(
        id=response.json()['id'], **payload
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_exercise_order_sentence_distractors(
    client, generate_payload, token_header
):
    payload = generate_payload(exercise_factory.OrderSentenceFactory)
    terms = TermFactory.create_batch(size=5)
    term_ids = [term.id for term in terms]
    payload['additional_content'] = {'distractors': {'term': term_ids}}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    exercise = Exercise.objects.get(id=response.json()['id'])
    assert exercise.additional_content['distractors']['term'] == term_ids


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_exercise_order_sentence_invalid_distractors(
    client, generate_payload, token_header
):
    payload = generate_payload(exercise_factory.OrderSentenceFactory)
    term_ids = list(range(1000, 1009))
    payload['additional_content'] = {'distractors': {'term': term_ids}}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    exercise = Exercise.objects.get(id=response.json()['id'])
    assert exercise.additional_content['distractors']['term'] == []


def test_create_exercise_not_autenticated(client, generate_payload):
    payload = generate_payload(exercise_factory.OrderSentenceFactory)

    response = client.post(
        create_exercise_router,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_exercise_permission_denied(client, generate_payload, token_header):
    payload = generate_payload(exercise_factory.OrderSentenceFactory)

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 403


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@parametrize_exercies
def test_create_exercise_already_exists(
    client,
    generate_payload,
    token_header,
    exercise_factory,
):
    payload = generate_payload(exercise_factory)
    exercise_factory(**payload)

    response = client.post(
        create_exercise_router,
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 409


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factory.OrderSentenceFactory,
        exercise_factory.ListenSentenceFactory,
        exercise_factory.SpeakSentenceFactory,
    ],
)
def test_create_exercise_create_term_example_level(
    client, generate_payload, token_header, exercise_factory
):
    term_example = TermExampleFactory(level=Level.ADVANCED)
    payload = generate_payload(
        exercise_factory,
        term_example=term_example,
    )

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert ExerciseLevel.objects.filter(
        exercise_id=response.json()['id'],
        level=Level.ADVANCED,
    ).exists()


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factory.OrderSentenceFactory,
        exercise_factory.ListenSentenceFactory,
        exercise_factory.SpeakSentenceFactory,
    ],
)
def test_create_exercise_create_term_example_has_no_level(
    client, generate_payload, token_header, exercise_factory
):
    term_example = TermExampleFactory(level=None)
    payload = generate_payload(
        exercise_factory,
        term_example=term_example,
    )

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert not ExerciseLevel.objects.filter(
        exercise_id=response.json()['id'],
    ).exists()


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factory.ListenTermFactory,
        exercise_factory.ListenTermMChoiceFactory,
        exercise_factory.SpeakTermFactory,
        exercise_factory.TermMChoiceFactory,
    ],
)
def test_create_exercise_create_term_level(
    client, generate_payload, token_header, exercise_factory
):
    term = TermFactory()
    TermDefinitionFactory(
        level=Level.ADVANCED,
        term=term,
    )
    payload = generate_payload(
        exercise_factory,
        term=term,
    )

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert ExerciseLevel.objects.filter(
        exercise_id=response.json()['id'],
        level=Level.ADVANCED,
    ).exists()


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_exercise_create_term_definition_level(
    client, generate_payload, token_header
):
    term = TermFactory()
    term_definition = TermDefinitionFactory(term=term, level=Level.ADVANCED)

    payload = generate_payload(
        exercise_factory.TermDefinitionMChoiceFactory,
        term=term,
        term_definition=term_definition,
    )

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert ExerciseLevel.objects.filter(
        exercise_id=response.json()['id'],
        level=Level.ADVANCED,
    ).exists()
