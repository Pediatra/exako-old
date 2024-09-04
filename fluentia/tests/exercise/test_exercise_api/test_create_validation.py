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
        'term_example reference in term_pronunciation does not match.'
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
        'term_id reference in term_pronunciation does not match.'
        in response.json()['detail']
    )


@pytest.mark.parametrize(
    'exercise_factory',
    [
        exercise_factories.ListenTermLexicalFactory,
        exercise_factories.SpeakTermLexicalFactory,
        exercise_factories.TermLexicalMChoiceFactory,
    ],
)
def test_create_exercise_term_lexical_invalid_term_reference(
    client, generate_payload, token_header, exercise_factory
):
    term_lexical = TermLexicalFactory()
    payload = generate_payload(exercise_factory, term_lexical=term_lexical)

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'term_id reference in term_lexical does not match.' in response.json()['detail']
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
        'term_id reference in term_definition does not match.'
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
        'term_id reference in term_image does not match.' in response.json()['detail']
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
    assert 'pronunciation audio is not defined' in response.json()['detail']


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


def test_create_order_sentence_exercise_invalid_distractors_format(
    client, token_header, generate_payload
):
    payload = generate_payload(exercise_factories.OrderSentenceFactory)
    payload['additional_content']['distractors'] = 1

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


def test_create_term_mchoice_exercise_invalid_distractors(
    client, generate_payload, token_header
):
    payload = generate_payload(exercise_factories.TermMChoiceFactory)
    terms_ids = list(range(1000, 1009))
    payload['additional_content']['distractors'] = terms_ids

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


@pytest.mark.parametrize('additional_content', [{}, {'distractors': 1}])
def test_create_term_mchoice_exercise_invalid_distractors_format(
    client, generate_payload, token_header, additional_content
):
    payload = generate_payload(exercise_factories.TermMChoiceFactory)
    payload['additional_content'] = additional_content

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'invalid distractors format, exercise needs distractors to form the alternatives.'
        in response.json()['detail'][0]['msg']
    )


def test_create_term_definition_mchoice_exercise_invalid_distractors(
    client, generate_payload, token_header
):
    payload = generate_payload(exercise_factories.TermDefinitionMChoiceFactory)
    terms_ids = list(range(1000, 1009))
    payload['additional_content']['distractors'] = terms_ids

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


@pytest.mark.parametrize('additional_content', [{}, {'distractors': 1}])
def test_create_term_definition_mchoice_exercise_invalid_distractors_format(
    client, generate_payload, token_header, additional_content
):
    payload = generate_payload(exercise_factories.TermDefinitionMChoiceFactory)
    payload['additional_content'] = additional_content

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'invalid distractors format, exercise needs distractors to form the alternatives.'
        in response.json()['detail'][0]['msg']
    )


def test_create_term_image_mchoice_exercise_invalid_distractors(
    client, generate_payload, token_header
):
    payload = generate_payload(exercise_factories.TermImageMChoiceFactory)
    terms_ids = list(range(1000, 1009))
    payload['additional_content']['distractors'] = terms_ids

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


@pytest.mark.parametrize('additional_content', [{}, {'distractors': 1}])
def test_create_term_image_mchoice_exercise_invalid_distractors_format(
    client, generate_payload, token_header, additional_content
):
    payload = generate_payload(exercise_factories.TermImageMChoiceFactory)
    payload['additional_content'] = additional_content

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'invalid distractors format, exercise needs distractors to form the alternatives.'
        in response.json()['detail'][0]['msg']
    )


def test_create_term_image_text_mchoice_exercise_invalid_distractors(
    client, generate_payload, token_header
):
    payload = generate_payload(exercise_factories.TermImageMChoiceTextFactory)
    terms_ids = list(range(1000, 1009))
    payload['additional_content']['distractors'] = terms_ids

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


@pytest.mark.parametrize('additional_content', [{}, {'distractors': 1}])
def test_create_term_image_text_mchoice_exercise_invalid_distractors_format(
    client, generate_payload, token_header, additional_content
):
    payload = generate_payload(exercise_factories.TermImageMChoiceTextFactory)
    payload['additional_content'] = additional_content

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        'invalid distractors format, exercise needs distractors to form the alternatives.'
        in response.json()['detail'][0]['msg']
    )


def test_create_term_connection_exercise_invalid_distractors(
    client, generate_payload, token_header
):
    payload = generate_payload(exercise_factories.TermConnectionFactory)
    term_ids = list(range(1000, 1009))
    payload['additional_content']['distractors'] = term_ids

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'exercise needs at least 8 additional_content[distractors] to form the connections.'
    )


def test_create_term_connection_exercise_invalid_connections(
    client, generate_payload, token_header
):
    payload = generate_payload(exercise_factories.TermConnectionFactory)
    term_ids = list(range(1000, 1009))
    payload['additional_content']['connections'] = term_ids

    response = client.post(
        create_exercise_router,
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 422
    assert (
        response.json()['detail']
        == 'exercise needs at least 4 additional_content[connections] to form the connections.'
    )


@pytest.mark.parametrize('additional_content', [{}, {'distractors': 1}])
def test_create_term_connection_exercise_invalid_distractors_format(
    client, generate_payload, token_header, additional_content
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
        'invalid distractors format, exercise needs distractors to form the connections.'
        in response.json()['detail'][0]['msg']
    )


@pytest.mark.parametrize(
    'additional_content', [{'distractors': []}, {'distractors': [], 'connections': 1}]
)
def test_create_term_connection_exercise_invalid_connections_format(
    client, generate_payload, token_header, additional_content
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
