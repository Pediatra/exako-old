from random import choice, random
from urllib.parse import parse_qsl, urlencode, urlparse

import pytest
from django.urls import reverse_lazy

from exako.apps.exercise.api.schema import ExerciseView
from exako.apps.exercise.models import ExerciseLevel
from exako.apps.term.constants import Language, Level
from exako.tests.factories import exercise as exercise_factory
from exako.tests.factories.card import CardFactory, CardSetFactory

pytestmark = pytest.mark.django_db


def list_exercise_router(
    language,
    exercise_type=None,
    level=None,
    cardset_id=None,
    seed=None,
):
    params = {
        'language': language,
        'exercise_type': exercise_type,
        'level': level,
        'cardset_id': cardset_id,
        'seed': seed,
    }
    url = str(reverse_lazy('api-1.0.0:list_exercise'))
    parsed_url = urlparse(url)

    query_params = parse_qsl(parsed_url.query)

    for key, values in params.items():
        if values is None:
            continue
        if isinstance(values, list):
            for value in values:
                query_params.append((key, value))
        else:
            query_params.append((key, values))

    new_query = urlencode(query_params)
    new_url = parsed_url._replace(query=new_query).geturl()

    return new_url


parametrize_exercies = pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factory.OrderSentenceFactory,
        exercise_factory.ListenTermFactory,
        exercise_factory.ListenTermLexicalFactory,
        exercise_factory.ListenTermLexicalTermRefFactory,
        exercise_factory.ListenSentenceFactory,
        exercise_factory.ListenTermMChoiceFactory,
        exercise_factory.SpeakTermFactory,
        exercise_factory.SpeakTermLexicalFactory,
        exercise_factory.SpeakTermLexicalTermRefFactory,
        exercise_factory.SpeakSentenceFactory,
        exercise_factory.TermMChoiceFactory,
        exercise_factory.TermMChoiceLexicalFactory,
        exercise_factory.TermMChoiceLexicalTermRefFactory,
        exercise_factory.TermDefinitionMChoiceFactory,
        exercise_factory.TermImageMChoiceFactory,
        exercise_factory.TermImageMChoiceTextFactory,
        exercise_factory.TermConnectionFactory,
    ],
)


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@parametrize_exercies
@pytest.mark.parametrize(
    'language',
    [
        [Language.PORTUGUESE],
        [Language.PORTUGUESE, Language.CHINESE, Language.JAPANESE],
    ],
)
def test_list_exercise(client, token_header, exercise_factory, language):
    exercises = [exercise_factory(language=choice(language)) for _ in range(10)]
    exercise_factory.create_batch(language=Language.ENGLISH, size=5)

    response = client.get(
        list_exercise_router(language=language),
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['count'] == 10
    exercise_schema_view = [ExerciseView.from_orm(exercise) for exercise in exercises]
    for item in response.json()['items']:
        assert ExerciseView(**item) in exercise_schema_view


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@pytest.mark.parametrize(
    'factories',
    [
        (
            exercise_factory.OrderSentenceFactory,
            exercise_factory.SpeakTermFactory,
            exercise_factory.TermImageMChoiceTextFactory,
            exercise_factory.ListenSentenceFactory,
            3,
        ),
        (
            exercise_factory.ListenTermFactory,
            exercise_factory.TermDefinitionMChoiceFactory,
            exercise_factory.SpeakSentenceFactory,
            exercise_factory.OrderSentenceFactory,
            3,
        ),
        (
            exercise_factory.ListenTermLexicalFactory,
            exercise_factory.TermDefinitionMChoiceFactory,
            exercise_factory.SpeakSentenceFactory,
            exercise_factory.OrderSentenceFactory,
            3,
        ),
        (
            exercise_factory.ListenTermLexicalTermRefFactory,
            exercise_factory.TermDefinitionMChoiceFactory,
            exercise_factory.SpeakSentenceFactory,
            exercise_factory.OrderSentenceFactory,
            3,
        ),
        (
            exercise_factory.ListenSentenceFactory,
            exercise_factory.TermConnectionFactory,
            exercise_factory.TermMChoiceFactory,
            exercise_factory.ListenTermMChoiceFactory,
            3,
        ),
        (
            exercise_factory.ListenTermMChoiceFactory,
            exercise_factory.TermImageMChoiceFactory,
            exercise_factory.OrderSentenceFactory,
            exercise_factory.TermDefinitionMChoiceFactory,
            3,
        ),
        (
            exercise_factory.SpeakTermFactory,
            exercise_factory.ListenTermFactory,
            exercise_factory.TermImageMChoiceTextFactory,
            exercise_factory.TermConnectionFactory,
            3,
        ),
        (
            exercise_factory.SpeakTermLexicalFactory,
            exercise_factory.ListenTermFactory,
            exercise_factory.TermImageMChoiceTextFactory,
            exercise_factory.TermConnectionFactory,
            3,
        ),
        (
            exercise_factory.SpeakTermLexicalTermRefFactory,
            exercise_factory.ListenTermFactory,
            exercise_factory.TermImageMChoiceTextFactory,
            exercise_factory.TermConnectionFactory,
            3,
        ),
        (
            exercise_factory.SpeakSentenceFactory,
            exercise_factory.TermMChoiceFactory,
            exercise_factory.ListenTermMChoiceFactory,
            exercise_factory.TermImageMChoiceFactory,
            3,
        ),
        (
            exercise_factory.TermMChoiceFactory,
            exercise_factory.SpeakSentenceFactory,
            exercise_factory.ListenSentenceFactory,
            exercise_factory.OrderSentenceFactory,
            3,
        ),
        (
            exercise_factory.TermMChoiceLexicalFactory,
            exercise_factory.SpeakSentenceFactory,
            exercise_factory.ListenSentenceFactory,
            exercise_factory.OrderSentenceFactory,
            3,
        ),
        (
            exercise_factory.TermMChoiceLexicalTermRefFactory,
            exercise_factory.SpeakSentenceFactory,
            exercise_factory.ListenSentenceFactory,
            exercise_factory.OrderSentenceFactory,
            3,
        ),
        (
            exercise_factory.TermDefinitionMChoiceFactory,
            exercise_factory.ListenTermFactory,
            exercise_factory.SpeakTermFactory,
            exercise_factory.TermImageMChoiceTextFactory,
            3,
        ),
        (
            exercise_factory.TermImageMChoiceFactory,
            exercise_factory.TermConnectionFactory,
            exercise_factory.SpeakSentenceFactory,
            exercise_factory.ListenTermMChoiceFactory,
            3,
        ),
        (
            exercise_factory.TermImageMChoiceTextFactory,
            exercise_factory.OrderSentenceFactory,
            exercise_factory.ListenTermFactory,
            exercise_factory.TermMChoiceFactory,
            3,
        ),
        (
            exercise_factory.TermConnectionFactory,
            exercise_factory.SpeakTermFactory,
            exercise_factory.TermDefinitionMChoiceFactory,
            exercise_factory.ListenSentenceFactory,
            3,
        ),
        (
            exercise_factory.OrderSentenceFactory,
            exercise_factory.SpeakTermFactory,
            1,
        ),
        (
            exercise_factory.ListenTermFactory,
            exercise_factory.TermDefinitionMChoiceFactory,
            1,
        ),
        (
            exercise_factory.ListenTermLexicalFactory,
            exercise_factory.TermDefinitionMChoiceFactory,
            1,
        ),
        (
            exercise_factory.ListenTermLexicalTermRefFactory,
            exercise_factory.TermDefinitionMChoiceFactory,
            1,
        ),
        (
            exercise_factory.ListenSentenceFactory,
            exercise_factory.TermConnectionFactory,
            1,
        ),
        (
            exercise_factory.ListenTermMChoiceFactory,
            exercise_factory.TermImageMChoiceFactory,
            1,
        ),
        (
            exercise_factory.SpeakTermFactory,
            exercise_factory.ListenTermFactory,
            1,
        ),
        (
            exercise_factory.SpeakTermLexicalFactory,
            exercise_factory.ListenTermFactory,
            1,
        ),
        (
            exercise_factory.SpeakTermLexicalTermRefFactory,
            exercise_factory.ListenTermFactory,
            1,
        ),
        (
            exercise_factory.SpeakSentenceFactory,
            exercise_factory.TermMChoiceFactory,
            1,
        ),
        (
            exercise_factory.TermMChoiceFactory,
            exercise_factory.SpeakSentenceFactory,
            1,
        ),
        (
            exercise_factory.TermMChoiceLexicalFactory,
            exercise_factory.SpeakSentenceFactory,
            1,
        ),
        (
            exercise_factory.TermMChoiceLexicalTermRefFactory,
            exercise_factory.SpeakSentenceFactory,
            1,
        ),
        (
            exercise_factory.TermDefinitionMChoiceFactory,
            exercise_factory.ListenTermFactory,
            1,
        ),
        (
            exercise_factory.TermImageMChoiceFactory,
            exercise_factory.TermConnectionFactory,
            1,
        ),
        (
            exercise_factory.TermImageMChoiceTextFactory,
            exercise_factory.OrderSentenceFactory,
            1,
        ),
        (
            exercise_factory.TermConnectionFactory,
            exercise_factory.SpeakTermFactory,
            1,
        ),
    ],
)
def test_list_exercise_filter_exercise_type(client, token_header, factories):
    *exercise_factories, exercise_distractor_factory, count = factories
    exercises = [
        factory(language=Language.PORTUGUESE) for factory in exercise_factories
    ]
    exercise_distractor_factory.create_batch(
        size=5,
        language=Language.PORTUGUESE,
    )

    response = client.get(
        list_exercise_router(
            language=Language.PORTUGUESE,
            exercise_type=[exercise.type for exercise in exercises],
        ),
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['count'] == count
    exercise_schema_view = [ExerciseView.from_orm(exercise) for exercise in exercises]
    for item in response.json()['items']:
        assert ExerciseView(**item) in exercise_schema_view


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@parametrize_exercies
@pytest.mark.parametrize(
    'level',
    [
        [Level.ADVANCED],
        [Level.ADVANCED, Level.ELEMENTARY, Level.INTERMEDIATE],
    ],
)
def test_list_exercise_filter_level(client, token_header, exercise_factory, level):
    exercises1 = exercise_factory.create_batch(size=10, language=Language.PORTUGUESE)
    exercises2 = exercise_factory.create_batch(size=5, language=Language.PORTUGUESE)
    ExerciseLevel.objects.all().delete()
    [
        ExerciseLevel.objects.get_or_create(exercise=exercise, level=choice(level))
        for exercise in exercises1
    ]
    [
        ExerciseLevel.objects.get_or_create(exercise=exercise, level=Level.BEGINNER)
        for exercise in exercises2
    ]

    response = client.get(
        list_exercise_router(language=Language.PORTUGUESE, level=level),
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['count'] == 10
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
        exercise_factory.TermImageMChoiceFactory,
        exercise_factory.TermImageMChoiceTextFactory,
        exercise_factory.TermConnectionFactory,
    ],
)
def test_list_exercise_filter_cardset(client, user, token_header, exercise_factory):
    exercises_card = exercise_factory.create_batch(
        size=5,
        language=Language.PORTUGUESE,
    )
    cardset = CardSetFactory(user=user)
    [
        CardFactory(
            cardset_id=cardset.id,
            term=exercise.term,
        )
        for exercise in exercises_card
    ]
    exercises = exercise_factory.create_batch(size=5, language=Language.PORTUGUESE)

    response = client.get(
        list_exercise_router(
            language=Language.PORTUGUESE,
            cardset_id=cardset.id,
        ),
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['count'] == 10
    assert all(
        [
            ExerciseView.from_orm(exercise)
            in [ExerciseView(**resp) for resp in response.json()['items'][:5]]
            for exercise in exercises_card
        ]
    )
    exercise_schema_response = [
        ExerciseView.from_orm(exercise) for exercise in exercises
    ]
    for item in response.json()['items'][5:]:
        assert ExerciseView(**item) in exercise_schema_response


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factory.ListenTermLexicalFactory,
        exercise_factory.SpeakTermLexicalFactory,
        exercise_factory.TermMChoiceLexicalFactory,
    ],
)
def test_list_exercise_filter_cardset_term_lexical_value(
    client, user, token_header, exercise_factory
):
    exercises_card = exercise_factory.create_batch(
        size=5,
        language=Language.PORTUGUESE,
    )
    cardset = CardSetFactory(user=user)
    [
        CardFactory(
            cardset_id=cardset.id,
            term=exercise.term_lexical.term,
        )
        for exercise in exercises_card
    ]
    exercises = exercise_factory.create_batch(size=5, language=Language.PORTUGUESE)

    response = client.get(
        list_exercise_router(
            language=Language.PORTUGUESE,
            cardset_id=cardset.id,
        ),
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['count'] == 10
    assert all(
        [
            ExerciseView.from_orm(exercise)
            in [ExerciseView(**resp) for resp in response.json()['items'][:5]]
            for exercise in exercises_card
        ]
    )
    exercise_schema_response = [
        ExerciseView.from_orm(exercise) for exercise in exercises
    ]
    for item in response.json()['items'][5:]:
        assert ExerciseView(**item) in exercise_schema_response


@pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True)
@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factory.ListenTermLexicalTermRefFactory,
        exercise_factory.SpeakTermLexicalTermRefFactory,
        exercise_factory.TermMChoiceLexicalTermRefFactory,
    ],
)
def test_list_exercise_filter_cardset_term_lexical_term_ref(
    client, user, token_header, exercise_factory
):
    exercises_card = exercise_factory.create_batch(
        size=5,
        language=Language.PORTUGUESE,
    )
    cardset = CardSetFactory(user=user)
    [
        CardFactory(
            cardset_id=cardset.id,
            term=exercise.term_lexical.term_value_ref,
        )
        for exercise in exercises_card
    ]
    exercises = exercise_factory.create_batch(size=5, language=Language.PORTUGUESE)

    response = client.get(
        list_exercise_router(
            language=Language.PORTUGUESE,
            cardset_id=cardset.id,
        ),
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['count'] == 10
    assert all(
        [
            ExerciseView.from_orm(exercise)
            in [ExerciseView(**resp) for resp in response.json()['items'][:5]]
            for exercise in exercises_card
        ]
    )
    exercise_schema_response = [
        ExerciseView.from_orm(exercise) for exercise in exercises
    ]
    for item in response.json()['items'][5:]:
        assert ExerciseView(**item) in exercise_schema_response


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
