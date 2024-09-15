import pytest
from django.urls import reverse_lazy

from fluentia.apps.exercise.constants import ExerciseType
from fluentia.apps.term.constants import TermLexicalType
from fluentia.apps.term.models import TermExampleLink, TermLexical
from fluentia.tests.factories import exercise as exercise_factories
from fluentia.tests.factories.term import (
    TermDefinitionFactory,
    TermExampleFactory,
    TermFactory,
    TermImageFactory,
    TermLexicalFactory,
    TermPronunciationFactory,
)

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.parametrize('user', [{'is_superuser': True}], indirect=True),
]


create_exercise_router = reverse_lazy('api-1.0.0:create_exercise')


def test_create_listen_sentence_exercise_invalid_term_reference(
    client, generate_payload, token_header
):
    term_example = TermExampleFactory()
    term_pronunciation = TermPronunciationFactory(term_example=TermExampleFactory())
    payload = generate_payload(
        exercise_factories.ListenSentenceFactory,
        term_example=term_example,
        term_pronunciation=term_pronunciation,
    )

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'term_example_id reference in term_pronunciation_id does not match.'
        in response.json()['detail']
    )


@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factories.ListenTermFactory,
        exercise_factories.ListenTermMChoiceFactory,
        exercise_factories.TermImageMChoiceFactory,
    ],
)
def test_create_exercise_term_pronunciation_invalid_term_reference(
    client, generate_payload, token_header, exercise_factory
):
    term_pronunciation = TermPronunciationFactory()
    payload = generate_payload(exercise_factory, term_pronunciation=term_pronunciation)

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'term_id reference in term_pronunciation_id does not match.'
        in response.json()['detail']
    )


def test_create_term_definition_mchoice_exercise_invalid_term_definition_reference(
    client, generate_payload, token_header
):
    term_definition = TermDefinitionFactory()
    payload = generate_payload(
        exercise_factories.TermDefinitionMChoiceFactory,
        term_definition=term_definition,
    )

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'term_id reference in term_definition_id does not match.'
        in response.json()['detail']
    )


@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factories.TermImageMChoiceFactory,
        exercise_factories.TermImageMChoiceTextFactory,
    ],
)
def test_create_exercise_term_image_invalid_term_reference(
    client, generate_payload, token_header, exercise_factory
):
    term_image = TermImageFactory()
    payload = generate_payload(exercise_factory, term_image=term_image)

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'term_id reference in term_image_id does not match.'
        in response.json()['detail']
    )


@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factories.ListenTermFactory,
        exercise_factories.ListenSentenceFactory,
        exercise_factories.ListenTermMChoiceFactory,
        exercise_factories.TermImageMChoiceFactory,
    ],
)
def test_create_exercise_listen_exercise_none(
    client, generate_payload, token_header, exercise_factory
):
    term = TermFactory()
    term_example = TermExampleFactory()
    term_pronunciation = TermPronunciationFactory(
        term_example=term_example,
        term=term,
        audio_file=None,
    )
    payload = generate_payload(
        exercise_factory,
        term=term,
        term_example=term_example,
        term_pronunciation=term_pronunciation,
    )

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert 'pronunciation audio file is required.' in response.json()['detail']


def test_create_exercise_listen_mchoice_without_rhyme(
    client, generate_payload, token_header
):
    term = TermFactory()
    payload = generate_payload(
        exercise_factories.ListenTermMChoiceFactory,
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


def test_create_exercise_listen_mchoice_without_audio_file_rhyme(
    client, generate_payload, token_header
):
    term = TermFactory()
    payload = generate_payload(
        exercise_factories.ListenTermMChoiceFactory,
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


def test_create_term_mchoice_exercise_without_example_highlight(
    client, token_header, generate_payload
):
    payload = generate_payload(exercise_factories.TermMChoiceFactory)
    TermExampleLink.objects.all().delete()

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'term mchoice exercise need term_example with highlight link.'
        in response.json()['detail']
    )


def test_create_term_lexical_mchoice_exercise_without_example_highlight(
    client, token_header, generate_payload
):
    payload = generate_payload(exercise_factories.TermLexicalMChoiceFactory)
    TermExampleLink.objects.all().delete()

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'term mchoice exercise need term_example with highlight link.'
        in response.json()['detail']
    )


def test_create_order_sentence_exercise_invalid_distractor_format_is_not_a_list(
    client, token_header, generate_payload
):
    payload = generate_payload(exercise_factories.OrderSentenceFactory)
    payload['additional_content'] = {'distractors': {'term': 1}}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'invalid distractors format, it should be a id list.'
        in response.json()['detail'][0]['msg']
    )


@pytest.mark.parametrize(
    'factory, additional_content',
    [
        (exercise_factories.TermMChoiceFactory, {}),
        (exercise_factories.TermLexicalMChoiceFactory, {}),
        (exercise_factories.TermDefinitionMChoiceFactory, {}),
        (exercise_factories.TermImageMChoiceFactory, {}),
        (exercise_factories.TermImageMChoiceTextFactory, {}),
        (exercise_factories.TermConnectionFactory, {}),
        (exercise_factories.TermMChoiceFactory, {'distractors': {}}),
        (exercise_factories.TermMChoiceFactory, {'distractors': {'term_lexical': []}}),
        (exercise_factories.TermLexicalMChoiceFactory, {'distractors': {}}),
        (exercise_factories.TermLexicalMChoiceFactory, {'distractors': {'term': []}}),
        (exercise_factories.TermDefinitionMChoiceFactory, {'distractors': {}}),
        (exercise_factories.TermImageMChoiceFactory, {'distractors': {}}),
        (exercise_factories.TermImageMChoiceTextFactory, {'distractors': {}}),
        (exercise_factories.TermConnectionFactory, {'distractors': {}}),
    ],
)
def test_create_exercise_invalid_distractor_format(
    client, token_header, generate_payload, factory, additional_content
):
    payload = generate_payload(factory)
    payload['additional_content'] = additional_content

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'invalid distractors format, exercise needs'
        in response.json()['detail'][0]['msg']
    )


@pytest.mark.parametrize(
    'factory, additional_content',
    [
        (exercise_factories.TermMChoiceFactory, {'distractors': {'term': 1}}),
        (
            exercise_factories.TermLexicalMChoiceFactory,
            {'distractors': {'term_lexical': 1}},
        ),
        (
            exercise_factories.TermDefinitionMChoiceFactory,
            {'distractors': {'term_definition': 1}},
        ),
        (
            exercise_factories.TermImageMChoiceFactory,
            {'distractors': {'term_image': 1}},
        ),
        (exercise_factories.TermImageMChoiceTextFactory, {'distractors': {'term': 1}}),
        (exercise_factories.TermConnectionFactory, {'distractors': {'term': 1}}),
    ],
)
def test_create_exercise_invalid_distractor_format_is_not_a_list(
    client, token_header, generate_payload, factory, additional_content
):
    payload = generate_payload(factory)
    payload['additional_content'] = additional_content

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'invalid distractors format, it should be a id list.'
        in response.json()['detail'][0]['msg']
    )


@pytest.mark.parametrize(
    'additional_content',
    [{}, {'connections': {}}],
)
def test_create_term_connection_exercise_invalid_connection_format(
    client, token_header, generate_payload, additional_content
):
    payload = generate_payload(exercise_factories.TermConnectionFactory)
    payload['additional_content'] = additional_content

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'invalid distractors format, exercise needs distractors to form'
        in response.json()['detail'][0]['msg']
    )


def test_create_term_connection_exercise_invalid_connection_format_is_not_a_list(
    client, token_header, generate_payload
):
    payload = generate_payload(exercise_factories.TermConnectionFactory)
    payload['additional_content'] = {'connections': {'term': 1}}

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'invalid distractors format, exercise needs distractors to form'
        in response.json()['detail'][0]['msg']
    )


@pytest.mark.parametrize(
    'factory, additional_content',
    [
        (
            exercise_factories.TermMChoiceFactory,
            {'distractors': {'term': list(range(1000, 1010))}},
        ),
        (
            exercise_factories.TermLexicalMChoiceFactory,
            {'distractors': {'term_lexical': list(range(1000, 1010))}},
        ),
        (
            exercise_factories.TermDefinitionMChoiceFactory,
            {'distractors': {'term_definition': list(range(1000, 1010))}},
        ),
        (
            exercise_factories.TermImageMChoiceFactory,
            {'distractors': {'term_image': list(range(1000, 1010))}},
        ),
        (
            exercise_factories.TermImageMChoiceTextFactory,
            {'distractors': {'term': list(range(1000, 1010))}},
        ),
    ],
)
def test_create_exercise_invalid_distractor(
    client, token_header, generate_payload, factory, additional_content
):
    payload = generate_payload(factory)
    payload['additional_content'].update(additional_content)

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert 'exercise needs at least' in response.json()['detail']


def test_create_term_connection_exercise_invalid_distractor(
    client, token_header, generate_payload
):
    payload = generate_payload(exercise_factories.TermConnectionFactory)
    payload['additional_content']['distractors']['term'] = list(range(1000, 1010))

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'exercise needs at least 8 additional_content[distractors]'
        in response.json()['detail']
    )


def test_create_term_connection_exercise_invalid_connection(
    client, token_header, generate_payload
):
    payload = generate_payload(exercise_factories.TermConnectionFactory)
    payload['additional_content']['connections']['term'] = list(range(1000, 1010))

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'exercise needs at least 4 additional_content[connections]'
        in response.json()['detail']
    )
