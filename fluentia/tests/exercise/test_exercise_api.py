from random import random

import pytest
from django.urls import reverse_lazy

from fluentia.apps.core.query import set_url_params
from fluentia.apps.exercise.api.schema import ExerciseSchemaView, ExerciseView
from fluentia.apps.exercise.constants import ExerciseType
from fluentia.apps.exercise.models import Exercise, ExerciseLevel
from fluentia.apps.term.constants import Language, Level, TermLexicalType
from fluentia.apps.term.models import TermLexical
from fluentia.tests.factories.card import CardFactory, CardSetFactory
from fluentia.tests.factories.exercise import (
    ListenSentenceFactory,
    ListenTermFactory,
    ListenTermMChoiceFactory,
    OrderSentenceFactory,
    SpeakSentenceFactory,
    SpeakTermFactory,
    TermDefinitionMChoiceFactory,
    TermMChoiceFactory,
)
from fluentia.tests.factories.term import (
    TermDefinitionFactory,
    TermExampleFactory,
    TermFactory,
    TermLexicalFactory,
    TermPronunciationFactory,
)

pytestmark = pytest.mark.django_db


create_exercise_router = reverse_lazy('api-1.0.0:create_exercise')


def list_exercise_router(
    language, exercise_type=None, level=None, cardset_id=None, seed=None
):
    url = str(reverse_lazy('api-1.0.0:list_exercise'))
    return set_url_params(
        url,
        language=language,
        exercise_type=exercise_type,
        level=level,
        cardset_id=cardset_id,
        seed=seed,
    )


parametrize_exercies = pytest.mark.parametrize(
    'exercise_factory',
    [
        OrderSentenceFactory,
        ListenTermFactory,
        ListenSentenceFactory,
        ListenTermMChoiceFactory,
        SpeakTermFactory,
        SpeakSentenceFactory,
        TermMChoiceFactory,
        TermDefinitionMChoiceFactory,
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
    payload = generate_payload(OrderSentenceFactory)
    terms = TermFactory.create_batch(size=5)
    term_ids = [term.id for term in terms]
    payload['additional_content'] = {'distractors': term_ids}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    exercise = Exercise.objects.get(id=response.json()['id'])
    assert exercise.additional_content['distractors'] == term_ids


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_exercise_order_sentence_invalid_distractors(
    client, generate_payload, token_header
):
    payload = generate_payload(OrderSentenceFactory)
    term_ids = list(range(5))
    payload['additional_content'] = {'distractors': term_ids}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    exercise = Exercise.objects.get(id=response.json()['id'])
    assert exercise.additional_content['distractors'] == []


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_mchoice_distractors(client, generate_payload, token_header):
    payload = generate_payload(TermMChoiceFactory)
    terms = TermFactory.create_batch(size=5)
    term_ids = [term.id for term in terms]
    payload['additional_content'] = {'distractors': term_ids}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    exercise = Exercise.objects.get(id=response.json()['id'])
    assert exercise.additional_content['distractors'] == term_ids


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_distractors(client, generate_payload, token_header):
    payload = generate_payload(TermDefinitionMChoiceFactory)
    terms = TermDefinitionFactory.create_batch(size=5)
    term_ids = [term.id for term in terms]
    payload['additional_content'] = {'distractors': term_ids}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 201
    exercise = Exercise.objects.get(id=response.json()['id'])
    assert exercise.additional_content['distractors'] == term_ids


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@pytest.mark.parametrize(
    'exercise_factory',
    [
        OrderSentenceFactory,
        ListenSentenceFactory,
        SpeakSentenceFactory,
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
        OrderSentenceFactory,
        ListenSentenceFactory,
        SpeakSentenceFactory,
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
        ListenTermFactory,
        ListenTermMChoiceFactory,
        SpeakTermFactory,
        TermMChoiceFactory,
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
    term_definition = TermDefinitionFactory(level=Level.ADVANCED)

    payload = generate_payload(
        TermDefinitionMChoiceFactory,
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


def test_create_exercise_not_autenticated(client, generate_payload):
    payload = generate_payload(OrderSentenceFactory)

    response = client.post(
        create_exercise_router,
        payload,
        content_type='application/json',
    )

    assert response.status_code == 401


def test_create_exercise_permission_denied(client, generate_payload, token_header):
    payload = generate_payload(OrderSentenceFactory)

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 403


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@parametrize_exercies
def test_create_exercise_not_found(
    client,
    generate_payload,
    token_header,
    exercise_factory,
):
    payload = generate_payload(exercise_factory)
    payload.update(
        term=23513516,
        term_example=61261617,
        term_pronunciation=123616767,
        term_definition=161256167,
    )

    response = client.post(
        create_exercise_router,
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 404


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
        ListenTermFactory,
        SpeakTermFactory,
        TermMChoiceFactory,
    ],
)
def test_create_exercise_term_lexical_is_not_form(
    client, generate_payload, token_header, exercise_factory
):
    term_lexical = TermLexicalFactory(type=TermLexicalType.ANTONYM)
    payload = generate_payload(
        exercise_factory,
        term_lexical=term_lexical,
    )

    response = client.post(
        create_exercise_router,
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 422
    assert (
        'exercise lexical only accepts TermLexicalType.FORM'
        in response.json()['detail']
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@pytest.mark.parametrize(
    'exercise_factory',
    [
        ListenTermFactory,
        ListenSentenceFactory,
        ListenTermMChoiceFactory,
    ],
)
def test_create_exercise_listen_exercise_none(
    client, generate_payload, token_header, exercise_factory
):
    term_pronunciation = TermPronunciationFactory(audio_file=None)
    payload = generate_payload(
        exercise_factory,
        term_pronunciation=term_pronunciation,
    )

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert 'pronunciation audio is not defined' in response.json()['detail']


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_exercise_listen_mchoice_without_rhyme(
    client, generate_payload, token_header
):
    term = TermFactory()
    payload = generate_payload(
        ListenTermMChoiceFactory,
        term=term,
    )
    TermLexical.objects.filter(term=term).delete()

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert 'mchoice exercises need to have at least 3' in response.json()['detail']


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_exercise_listen_mchoice_without_audio_file_rhyme(
    client, generate_payload, token_header
):
    term = TermFactory()
    payload = generate_payload(
        ListenTermMChoiceFactory,
        term=term,
    )
    TermLexical.objects.filter(term=term).delete()
    lexicals = TermLexicalFactory.create_batch(
        term=term,
        type=TermLexicalType.RHYME,
        size=3,
    )
    [
        TermPronunciationFactory(term=lexical.term_value_ref, audio_file=None)
        for lexical in lexicals
    ]

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert 'mchoice exercises need to have at least 3' in response.json()['detail']


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_exercise_invalid_exercise_type(client, token_header):
    payload = dict(type=ExerciseType.RANDOM)

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert 'invalid exercise type' in response.json()['detail'][0]['msg']


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_mchoice_distractors_invalid(
    client, generate_payload, token_header
):
    payload = generate_payload(TermMChoiceFactory)
    term_ids = [9180275125, 9517285901, 951725017, 981502197]
    payload['additional_content'] = {'distractors': term_ids}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'exercise needs at least 3 additional_content[distractors] to form the alternatives.'
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_mchoice_distractors_without_additional_content(
    client, generate_payload, token_header
):
    payload = generate_payload(TermMChoiceFactory)
    payload['additional_content'] = None

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'exercise needs at least 3 additional_content[distractors] to form the alternatives.'
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_mchoice_distractors_without_distractors(
    client, generate_payload, token_header
):
    payload = generate_payload(TermMChoiceFactory)
    payload['additional_content'] = {}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'exercise needs at least 3 additional_content[distractors] to form the alternatives.'
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_mchoice_distractors_invalid_distractors_format(
    client, generate_payload, token_header
):
    payload = generate_payload(TermMChoiceFactory)
    payload['additional_content'] = {'distractors': 12345}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'exercise needs at least 3 additional_content[distractors] to form the alternatives.'
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_distractors_invalid(
    client, generate_payload, token_header
):
    payload = generate_payload(TermDefinitionMChoiceFactory)
    term_ids = [9180275125, 9517285901, 951725017, 981502197]
    payload['additional_content'] = {'distractors': term_ids}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'exercise needs at least 3 additional_content[distractors] to form the alternatives.'
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_mchoice_distractors_without_additional_content(
    client, generate_payload, token_header
):
    payload = generate_payload(TermDefinitionMChoiceFactory)
    payload['additional_content'] = None

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'exercise needs at least 3 additional_content[distractors] to form the alternatives.'
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_mchoice_distractors_without_distractors(
    client, generate_payload, token_header
):
    payload = generate_payload(TermDefinitionMChoiceFactory)
    payload['additional_content'] = {}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'exercise needs at least 3 additional_content[distractors] to form the alternatives.'
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
def test_create_term_definition_mchoice_distractors_invalid_distractors_format(
    client, generate_payload, token_header
):
    payload = generate_payload(TermDefinitionMChoiceFactory)
    payload['additional_content'] = {'distractors': 12345}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'exercise needs at least 3 additional_content[distractors] to form the alternatives.'
    )


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@parametrize_exercies
def test_list_exercise(client, token_header, exercise_factory):
    exercises = exercise_factory.create_batch(size=5, language=Language.PORTUGUESE)
    exercise_factory.create_batch(language=Language.ENGLISH, size=5)

    response = client.get(
        list_exercise_router(language=Language.PORTUGUESE),
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['count'] == 5
    exercise_schema_view = [ExerciseView.from_orm(exercise) for exercise in exercises]
    for item in response.json()['items']:
        assert ExerciseView(**item) in exercise_schema_view


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@pytest.mark.parametrize(
    'factories',
    [
        (OrderSentenceFactory, ListenTermFactory),
        (ListenTermFactory, ListenSentenceFactory),
        (ListenSentenceFactory, ListenTermMChoiceFactory),
        (ListenTermMChoiceFactory, SpeakTermFactory),
        (SpeakTermFactory, SpeakSentenceFactory),
        (SpeakSentenceFactory, TermMChoiceFactory),
        (TermMChoiceFactory, TermDefinitionMChoiceFactory),
        (TermDefinitionMChoiceFactory, OrderSentenceFactory),
    ],
)
def test_list_exercise_filter_exercise_type(client, token_header, factories):
    exercise_factory, exercise_foo_factory = factories
    exercises = exercise_factory.create_batch(
        size=5,
        language=Language.PORTUGUESE,
    )
    exercise_foo_factory.create_batch(
        size=5,
        language=Language.PORTUGUESE,
    )

    response = client.get(
        list_exercise_router(
            language=Language.PORTUGUESE,
            exercise_type=exercises[0].type,
        ),
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['count'] == 5
    exercise_schema_view = [ExerciseView.from_orm(exercise) for exercise in exercises]
    for item in response.json()['items']:
        assert ExerciseView(**item) in exercise_schema_view


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@parametrize_exercies
def test_list_exercise_filter_level(client, token_header, exercise_factory):
    exercises1 = exercise_factory.create_batch(size=5, language=Language.PORTUGUESE)
    exercises2 = exercise_factory.create_batch(size=5, language=Language.PORTUGUESE)
    ExerciseLevel.objects.all().delete()
    [
        ExerciseLevel.objects.get_or_create(exercise=exercise, level=Level.ADVANCED)
        for exercise in exercises1
    ]
    [
        ExerciseLevel.objects.get_or_create(exercise=exercise, level=Level.BEGINNER)
        for exercise in exercises2
    ]

    response = client.get(
        list_exercise_router(language=Language.PORTUGUESE, level=Level.ADVANCED),
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['count'] == 5
    exercise_schema_view = [ExerciseView.from_orm(exercise) for exercise in exercises1]
    for item in response.json()['items']:
        assert ExerciseView(**item) in exercise_schema_view


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@pytest.mark.parametrize(
    'exercise_factory',
    [
        ListenTermFactory,
        ListenTermMChoiceFactory,
        SpeakTermFactory,
        TermMChoiceFactory,
    ],
)
def test_list_exercise_filter_cardset(client, user, token_header, exercise_factory):
    exercises = exercise_factory.create_batch(
        size=5,
        language=Language.PORTUGUESE,
    )
    cardset = CardSetFactory(user=user)
    [
        CardFactory(
            cardset_id=cardset.id,
            term=exercise.term,
        )
        for exercise in exercises
    ]
    exercise_factory.create_batch(size=5, language=Language.PORTUGUESE)

    response = client.get(
        list_exercise_router(
            language=Language.PORTUGUESE,
            cardset_id=cardset.id,
        ),
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['count'] == 5
    exercise_schema_view = [ExerciseView.from_orm(exercise) for exercise in exercises]
    for item in response.json()['items']:
        assert ExerciseView(**item) in exercise_schema_view


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@parametrize_exercies
def test_list_exercise_filter_seed(client, token_header, exercise_factory):
    exercises = exercise_factory.create_batch(
        size=5,
        language=Language.PORTUGUESE,
    )
    seed = random()

    response = client.get(
        list_exercise_router(
            language=Language.PORTUGUESE,
            exercise_type=exercises[0].type,
            seed=seed,
        ),
        headers=token_header,
    )

    response2 = client.get(
        list_exercise_router(
            language=Language.PORTUGUESE,
            exercise_type=exercises[0].type,
            seed=seed,
        ),
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json() == response2.json()
