from random import random

import pytest
from django.urls import reverse_lazy

from fluentia.apps.core.query import set_url_params
from fluentia.apps.exercise.api.schema import ExerciseView
from fluentia.apps.exercise.models import ExerciseLevel
from fluentia.apps.term.constants import Language, Level
from fluentia.tests.factories import exercise as exercise_factory
from fluentia.tests.factories.card import CardFactory, CardSetFactory

pytestmark = pytest.mark.django_db


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
        (exercise_factory.OrderSentenceFactory, exercise_factory.ListenTermFactory),
        (exercise_factory.ListenTermFactory, exercise_factory.ListenSentenceFactory),
        (
            exercise_factory.ListenSentenceFactory,
            exercise_factory.ListenTermMChoiceFactory,
        ),
        (exercise_factory.ListenTermMChoiceFactory, exercise_factory.SpeakTermFactory),
        (exercise_factory.SpeakTermFactory, exercise_factory.SpeakSentenceFactory),
        (exercise_factory.SpeakSentenceFactory, exercise_factory.TermMChoiceFactory),
        (
            exercise_factory.TermMChoiceFactory,
            exercise_factory.TermDefinitionMChoiceFactory,
        ),
        (
            exercise_factory.TermDefinitionMChoiceFactory,
            exercise_factory.OrderSentenceFactory,
        ),
        (
            exercise_factory.TermImageMChoiceFactory,
            exercise_factory.TermDefinitionMChoiceFactory,
        ),
        (
            exercise_factory.TermImageMChoiceTextFactory,
            exercise_factory.TermImageMChoiceFactory,
        ),
        (
            exercise_factory.TermConnectionFactory,
            exercise_factory.TermImageMChoiceTextFactory,
        ),
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
        exercise_factory.ListenTermFactory,
        exercise_factory.ListenTermMChoiceFactory,
        exercise_factory.SpeakTermFactory,
        exercise_factory.TermMChoiceFactory,
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
