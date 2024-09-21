import pytest
from django.urls import reverse_lazy

from exako.apps.exercise.constants import ExerciseSubType, ExerciseType
from exako.apps.term.constants import TermLexicalType
from exako.apps.term.models import TermExampleLink, TermLexical
from exako.tests.factories import exercise as exercise_factories
from exako.tests.factories.term import (
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
        exercise_factories.ListenTermLexicalFactory,
        exercise_factories.ListenTermLexicalTermRefFactory,
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
        'reference in term_pronunciation_id does not match.'
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
        exercise_factories.ListenTermMChoiceFactory,
        exercise_factories.TermImageMChoiceFactory,
    ],
)
def test_create_exercise_listen_term_exercise_none(
    client, generate_payload, token_header, exercise_factory
):
    term = TermFactory()
    term_pronunciation = TermPronunciationFactory(
        term=term,
        audio_file=None,
    )
    payload = generate_payload(
        exercise_factory,
        term=term,
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


def test_create_exercise_listen_listen_sentence_exercise_none(
    client, generate_payload, token_header
):
    term_example = TermExampleFactory()
    term_pronunciation = TermPronunciationFactory(
        term_example=term_example,
        audio_file=None,
    )
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
    assert 'pronunciation audio file is required.' in response.json()['detail']


@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factories.ListenTermLexicalFactory,
        exercise_factories.SpeakTermLexicalFactory,
    ],
)
def test_create_exercise_listen_term_lexical_value_exercise_none(
    client, generate_payload, token_header, exercise_factory
):
    term_lexical = TermLexicalFactory()
    term_pronunciation = TermPronunciationFactory(
        term_lexical=term_lexical,
        audio_file=None,
    )
    payload = generate_payload(
        exercise_factory,
        term_lexical=term_lexical,
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


@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factories.ListenTermLexicalTermRefFactory,
        exercise_factories.SpeakTermLexicalTermRefFactory,
    ],
)
def test_create_exercise_listen_term_lexical_term_ref_exercise_none(
    client, generate_payload, token_header, exercise_factory
):
    term_value_ref = TermFactory()
    term_lexical = TermLexicalFactory(value=None, term_value_ref=term_value_ref)
    term_pronunciation = TermPronunciationFactory(
        term=term_value_ref,
        audio_file=None,
    )
    payload = generate_payload(
        exercise_factory,
        term_lexical=term_lexical,
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


@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factories.TermMChoiceFactory,
        exercise_factories.TermMChoiceLexicalFactory,
        exercise_factories.TermMChoiceLexicalTermRefFactory,
    ],
)
def test_create_term_mchoice_exercise_without_example_highlight(
    client, token_header, generate_payload, exercise_factory
):
    payload = generate_payload(exercise_factory)
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
        (exercise_factories.TermMChoiceFactory, {'sub_type': ExerciseSubType.TERM}),
        (
            exercise_factories.TermMChoiceLexicalFactory,
            {'sub_type': ExerciseSubType.TERM_LEXICAL_VALUE},
        ),
        (
            exercise_factories.TermMChoiceLexicalTermRefFactory,
            {'sub_type': ExerciseSubType.TERM_LEXICAL_TERM_REF},
        ),
        (exercise_factories.TermDefinitionMChoiceFactory, {}),
        (exercise_factories.TermImageMChoiceFactory, {}),
        (exercise_factories.TermImageMChoiceTextFactory, {}),
        (exercise_factories.TermConnectionFactory, {}),
        (
            exercise_factories.TermMChoiceFactory,
            {'sub_type': ExerciseSubType.TERM, 'distractors': {}},
        ),
        (
            exercise_factories.TermMChoiceFactory,
            {'sub_type': ExerciseSubType.TERM, 'distractors': {'term_lexical': []}},
        ),
        (
            exercise_factories.TermMChoiceLexicalFactory,
            {'sub_type': ExerciseSubType.TERM_LEXICAL_VALUE, 'distractors': {}},
        ),
        (
            exercise_factories.TermMChoiceLexicalFactory,
            {
                'sub_type': ExerciseSubType.TERM_LEXICAL_VALUE,
                'distractors': {'term': []},
            },
        ),
        (
            exercise_factories.TermMChoiceLexicalTermRefFactory,
            {'sub_type': ExerciseSubType.TERM_LEXICAL_TERM_REF, 'distractors': {}},
        ),
        (
            exercise_factories.TermMChoiceLexicalTermRefFactory,
            {
                'sub_type': ExerciseSubType.TERM_LEXICAL_TERM_REF,
                'distractors': {'term': []},
            },
        ),
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
        (
            exercise_factories.TermMChoiceFactory,
            {'sub_type': ExerciseSubType.TERM, 'distractors': {'term': 1}},
        ),
        (
            exercise_factories.TermMChoiceLexicalFactory,
            {
                'sub_type': ExerciseSubType.TERM_LEXICAL_VALUE,
                'distractors': {'term_lexical': 1},
            },
        ),
        (
            exercise_factories.TermMChoiceLexicalTermRefFactory,
            {
                'sub_type': ExerciseSubType.TERM_LEXICAL_TERM_REF,
                'distractors': {'term_lexical': 1},
            },
        ),
        (
            exercise_factories.TermDefinitionMChoiceFactory,
            {'distractors': {'term_definition': 1}},
        ),
        (
            exercise_factories.TermImageMChoiceFactory,
            {'distractors': {'term_image': 1}},
        ),
        (
            exercise_factories.TermImageMChoiceTextFactory,
            {'distractors': {'term': 1}},
        ),
        (
            exercise_factories.TermConnectionFactory,
            {'distractors': {'term': 1}},
        ),
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
    [{'distractors': {'term': []}}, {'distractors': {'term': []}, 'connections': {}}],
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
        'invalid connections format, exercise needs connections to form the connections.'
        in response.json()['detail'][0]['msg']
    )


def test_create_term_connection_exercise_invalid_connection_format_is_not_a_list(
    client, token_header, generate_payload
):
    payload = generate_payload(exercise_factories.TermConnectionFactory)
    payload['additional_content'] = {
        'distractors': {'term': []},
        'connections': {'term': 1},
    }

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'invalid connections format, it should be a id list.'
        in response.json()['detail'][0]['msg']
    )


@pytest.mark.parametrize(
    'factory, additional_content',
    [
        (
            exercise_factories.TermMChoiceFactory,
            {
                'sub_type': ExerciseSubType.TERM,
                'distractors': {'term': list(range(1000, 1010))},
            },
        ),
        (
            exercise_factories.TermMChoiceLexicalFactory,
            {
                'sub_type': ExerciseSubType.TERM_LEXICAL_VALUE,
                'distractors': {'term_lexical': list(range(1000, 1010))},
            },
        ),
        (
            exercise_factories.TermMChoiceLexicalTermRefFactory,
            {
                'sub_type': ExerciseSubType.TERM_LEXICAL_TERM_REF,
                'distractors': {'term_lexical': list(range(1000, 1010))},
            },
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


@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factories.ListenTermFactory,
        exercise_factories.SpeakTermFactory,
        exercise_factories.TermMChoiceFactory,
    ],
)
def test_create_exercise_sub_type_field_not_defined(
    client, generate_payload, token_header, exercise_factory
):
    payload = generate_payload(exercise_factory)
    payload['term'] = None
    payload['term_lexical'] = None

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'provide term or term_lexical, but not both or neither.'
        in response.json()['detail'][0]['msg']
    )


@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factories.ListenTermFactory,
        exercise_factories.SpeakTermFactory,
        exercise_factories.TermMChoiceFactory,
    ],
)
def test_create_exercise_sub_type_field_both_fields(
    client, generate_payload, token_header, exercise_factory
):
    payload = generate_payload(exercise_factory)
    payload['term'] = 1
    payload['term_lexical'] = 1

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'provide term or term_lexical, but not both or neither.'
        in response.json()['detail'][0]['msg']
    )


@pytest.mark.parametrize(
    'exercise_factory, additional_content',
    [
        (exercise_factories.ListenTermFactory, None),
        (exercise_factories.SpeakTermFactory, None),
        (exercise_factories.ListenTermFactory, {}),
        (exercise_factories.SpeakTermFactory, {}),
        (exercise_factories.TermMChoiceFactory, {}),
        (exercise_factories.ListenTermFactory, {'sub_type': 10}),
        (exercise_factories.SpeakTermFactory, {'sub_type': 10}),
        (exercise_factories.TermMChoiceFactory, {'sub_type': 10}),
    ],
)
def test_create_exercise_sub_type_is_not_defined(
    client, generate_payload, token_header, exercise_factory, additional_content
):
    payload = generate_payload(exercise_factory)
    payload['additional_content'] = additional_content

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert 'sub type is not defined.' in response.json()['detail'][0]['msg']


@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factories.ListenTermFactory,
        exercise_factories.SpeakTermFactory,
        exercise_factories.TermMChoiceFactory,
    ],
)
def test_create_exercise_sub_type_term_invalid(
    client, generate_payload, token_header, exercise_factory
):
    payload = generate_payload(exercise_factory)
    payload['term'] = None
    payload['term_lexical'] = TermLexicalFactory().id

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert response.json()['detail'] == 'ExerciseSubType.TERM requires term'


@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factories.ListenTermLexicalFactory,
        exercise_factories.SpeakTermLexicalFactory,
        exercise_factories.TermMChoiceLexicalFactory,
    ],
)
def test_create_exercise_sub_type_term_lexical_value_invalid(
    client, generate_payload, token_header, exercise_factory
):
    payload = generate_payload(exercise_factory)
    TermLexical.objects.filter(id=payload['term_lexical']).update(value=None)

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'ExerciseSubType.TERM_LEXICAL_VALUE requires term_lexical.value'
    )


@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factories.ListenTermLexicalTermRefFactory,
        exercise_factories.SpeakTermLexicalTermRefFactory,
        exercise_factories.TermMChoiceLexicalTermRefFactory,
    ],
)
def test_create_exercise_sub_type_term_lexical_ref_invalid(
    client, generate_payload, token_header, exercise_factory
):
    payload = generate_payload(exercise_factory)
    TermLexical.objects.filter(id=payload['term_lexical']).update(term_value_ref=None)

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'ExerciseSubType.TERM_LEXICAL_TERM_REF requires term_lexical.term_value_ref'
    )
