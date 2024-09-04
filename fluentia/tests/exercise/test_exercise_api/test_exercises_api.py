from string import punctuation

import pytest
from django.db.models import OuterRef, Subquery
from django.urls import reverse_lazy

from fluentia.apps.exercise import constants
from fluentia.apps.term.constants import TermLexicalType
from fluentia.apps.term.models import (
    Term,
    TermDefinition,
    TermExampleLink,
    TermLexical,
    TermPronunciation,
)
from fluentia.tests.factories import exercise as exercise_factory
from fluentia.tests.factories.term import TermFactory, TermLexicalFactory

pytestmark = pytest.mark.django_db


def order_sentence_router(exercise_id):
    return reverse_lazy(
        'api-1.0.0:order_sentence_exercise', kwargs={'exercise_id': exercise_id}
    )


def listen_term_router(exercise_id):
    return reverse_lazy(
        'api-1.0.0:listen_term_exercise', kwargs={'exercise_id': exercise_id}
    )


def listen_term_mchoice_router(exercise_id):
    return reverse_lazy(
        'api-1.0.0:listen_term_mchoice_exercise', kwargs={'exercise_id': exercise_id}
    )


def listen_sentence_router(exercise_id):
    return reverse_lazy(
        'api-1.0.0:listen_sentence_exercise', kwargs={'exercise_id': exercise_id}
    )


def term_mchoice_router(exercise_id):
    return reverse_lazy(
        'api-1.0.0:term_mchoice_exercise', kwargs={'exercise_id': exercise_id}
    )


def term_definition_mchoice_router(exercise_id):
    return reverse_lazy(
        'api-1.0.0:term_definition_mchoice_exercise',
        kwargs={'exercise_id': exercise_id},
    )


def term_image_mchoice_router(exercise_id):
    return reverse_lazy(
        'api-1.0.0:term_image_mchoice_exercise',
        kwargs={'exercise_id': exercise_id},
    )


def test_order_sentence_exercise(client, token_header):
    exercise = exercise_factory.OrderSentenceFactory()

    response = client.get(order_sentence_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert response.json()['header'] == constants.ORDER_SENTENCE_HEADER
    sentence = exercise.term_example.example
    sentence = sentence.translate(str.maketrans('', '', punctuation))
    for part in sentence.split():  # pyright: ignore[reportGeneralTypeIssues]
        assert part in response.json()['sentence']
    distractors = Term.objects.filter(
        id__in=exercise.additional_content['distractors']
    ).values_list('expression', flat=True)
    assert any(item in response.json()['sentence'] for item in distractors)


def test_check_order_sentence_exercise_correct(client, token_header):
    exercise = exercise_factory.OrderSentenceFactory()
    payload = {
        'text': exercise.term_example.example.translate(
            str.maketrans('', '', punctuation)
        )
    }

    response = client.post(
        order_sentence_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True


def test_check_order_sentence_exercise_incorrect(client, token_header):
    exercise = exercise_factory.OrderSentenceFactory()
    payload = {'text': exercise.term_example.example + 'a'}

    response = client.post(
        order_sentence_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False


def test_listen_term_exercise(client, token_header):
    exercise = exercise_factory.ListenTermFactory()

    response = client.get(listen_term_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert response.json()['header'] == constants.LISTEN_TERM_HEADER
    assert response.json()['audio_file'] == exercise.term_pronunciation.audio_file


def test_check_listen_term_exercise_term(client, token_header):
    exercise = exercise_factory.ListenTermFactory()
    payload = {'text': exercise.term.expression}

    response = client.post(
        listen_term_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True


def test_check_listen_term_exercise_term_incorrect(client, token_header):
    exercise = exercise_factory.ListenTermFactory()
    payload = {'text': exercise.term.expression + 'a'}

    response = client.post(
        listen_term_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False


def test_check_listen_term_exercise_term_lexical_value_correct(client, token_header):
    exercise = exercise_factory.ListenTermLexicalFactory()
    payload = {'text': exercise.term_lexical.value}

    response = client.post(
        listen_term_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True


def test_check_listen_term_exercise_term_lexical_value_incorrect(client, token_header):
    exercise = exercise_factory.ListenTermLexicalFactory()
    payload = {'text': exercise.term_lexical.value + 'a'}

    response = client.post(
        listen_term_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False


def test_check_listen_term_exercise_term_lexical_term_value_ref_correct(
    client, token_header
):
    term_value_ref = TermFactory()
    term_lexical = TermLexicalFactory(value=None, term_value_ref=term_value_ref)
    exercise = exercise_factory.ListenTermFactory(
        term=term_lexical.term,
        term_lexical=term_lexical,
    )
    payload = {'text': term_value_ref.expression}

    response = client.post(
        listen_term_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True


def test_check_listen_term_exercise_term_lexical_term_value_ref_incorrect(
    client, token_header
):
    term_value_ref = TermFactory()
    term_lexical = TermLexicalFactory(value=None, term_value_ref=term_value_ref)
    exercise = exercise_factory.ListenTermFactory(
        term=term_lexical.term,
        term_lexical=term_lexical,
    )
    payload = {'text': term_value_ref.expression + 'a'}

    response = client.post(
        listen_term_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False


def test_listen_term_mchoice_exercise(client, token_header):
    exercise = exercise_factory.ListenTermMChoiceFactory()

    response = client.get(listen_term_mchoice_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert response.json()['header'] == constants.LISTEN_MCHOICE_HEADER
    assert len(response.json()['choices']) == 4
    alternatives = (
        TermLexical.objects.filter(
            term_id=exercise.term_id,
            type=TermLexicalType.RHYME,
            term_value_ref__isnull=False,
        )
        .select_related('term_value_ref')
        .annotate(
            audio_file=Subquery(
                TermPronunciation.objects.filter(
                    term_id=OuterRef('term_value_ref_id')
                ).values('audio_file')
            )
        )
        .values_list(
            'term_value_ref__expression',
            'audio_file',
        )[:3]
    )
    for expression, audio_file in alternatives:
        assert expression in response.json()['choices'].keys()
        assert audio_file in response.json()['choices'].values()
    assert exercise.term.expression in response.json()['choices'].keys()
    assert exercise.term_pronunciation.audio_file in response.json()['choices'].values()


def test_check_listen_term_mchoice_exercise_correct(client, token_header):
    exercise = exercise_factory.ListenTermMChoiceFactory()
    payload = {'text': exercise.term.expression}

    response = client.post(
        listen_term_mchoice_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct_answer'] == exercise.term.expression
    assert response.json()['correct'] is True


def test_check_listen_term_mchoice_exercise_incorrect(client, token_header):
    exercise = exercise_factory.ListenTermMChoiceFactory()
    payload = {'text': exercise.term.expression + 'a'}

    response = client.post(
        listen_term_mchoice_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct_answer'] == exercise.term.expression
    assert response.json()['correct'] is False


def test_listen_sentence_exercise(client, token_header):
    exercise = exercise_factory.ListenSentenceFactory()

    response = client.get(listen_sentence_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert response.json()['header'] == constants.LISTEN_SENTENCE_HEADER
    assert response.json()['audio_file'] == exercise.term_pronunciation.audio_file


def test_check_listen_sentence_exercise_correct(client, token_header):
    exercise = exercise_factory.ListenSentenceFactory()
    payload = {'text': exercise.term_example.example}

    response = client.post(
        listen_sentence_router(exercise.id),
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.json()['correct'] is True


def test_check_listen_sentence_exercise_incorrect(client, token_header):
    exercise = exercise_factory.ListenSentenceFactory()
    payload = {'text': exercise.term_example.example + 'a'}

    response = client.post(
        listen_sentence_router(exercise.id),
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.json()['correct'] is False


def test_term_mchoice_exercise_term(client, token_header):
    exercise = exercise_factory.TermMChoiceFactory()

    response = client.get(term_mchoice_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert len(response.json()['choices']) == 4
    assert exercise.term.expression in response.json()['choices']
    sentence = list(exercise.term_example.example)
    highlight = TermExampleLink.objects.filter(
        term_example_id=exercise.term_example_id,
        term_lexical_id=exercise.term_lexical_id,
    ).values_list('highlight', flat=True)[0]
    for start, end in list(highlight):
        for i in range(start, end + 1):
            sentence[i] = '_'
    sentence = ''.join(sentence)
    assert response.json()['header'] == constants.TERM_MCHOICE_HEADER.format(
        sentence=sentence
    )


def test_term_mchoice_exercise_term_lexical_value(client, token_header):
    exercise = exercise_factory.TermLexicalMChoiceFactory()

    response = client.get(term_mchoice_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert len(response.json()['choices']) == 4
    assert exercise.term_lexical.value in response.json()['choices']
    sentence = list(exercise.term_example.example)
    highlight = TermExampleLink.objects.filter(
        term_example_id=exercise.term_example_id,
        term_lexical_id=exercise.term_lexical_id,
    ).values_list('highlight', flat=True)[0]
    for start, end in list(highlight):
        for i in range(start, end + 1):
            sentence[i] = '_'
    sentence = ''.join(sentence)
    assert response.json()['header'] == constants.TERM_MCHOICE_HEADER.format(
        sentence=sentence
    )


def test_term_mchoice_exercise_term_lexical_term_value_ref(client, token_header):
    term_value_ref = TermFactory()
    term_lexical = TermLexicalFactory(value=None, term_value_ref=term_value_ref)
    exercise = exercise_factory.TermMChoiceFactory(
        term=term_lexical.term,
        term_lexical=term_lexical,
    )

    response = client.get(term_mchoice_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert len(response.json()['choices']) == 4
    assert term_value_ref.expression in response.json()['choices']
    sentence = list(exercise.term_example.example)
    highlight = TermExampleLink.objects.filter(
        term_example_id=exercise.term_example_id,
        term_lexical_id=exercise.term_lexical_id,
    ).values_list('highlight', flat=True)[0]
    for start, end in list(highlight):
        for i in range(start, end + 1):
            sentence[i] = '_'
    sentence = ''.join(sentence)
    assert response.json()['header'] == constants.TERM_MCHOICE_HEADER.format(
        sentence=sentence
    )


def test_check_term_mchoice_exercise_term_correct(client, token_header):
    exercise = exercise_factory.TermMChoiceFactory()
    payload = {'text': exercise.term.expression}

    response = client.post(
        term_mchoice_router(exercise.id),
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == exercise.term.expression


def test_check_term_mchoice_exercise_term_incorrect(client, token_header):
    exercise = exercise_factory.TermMChoiceFactory()
    payload = {'text': exercise.term.expression + 'a'}

    response = client.post(
        term_mchoice_router(exercise.id),
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == exercise.term.expression


def test_check_term_mchoice_exercise_term_lexical_value_correct(client, token_header):
    exercise = exercise_factory.TermLexicalMChoiceFactory()
    payload = {'text': exercise.term_lexical.value}

    response = client.post(
        term_mchoice_router(exercise.id),
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == exercise.term_lexical.value


def test_check_term_mchoice_exercise_term_lexical_value_incorrect(client, token_header):
    exercise = exercise_factory.TermLexicalMChoiceFactory()
    payload = {'text': exercise.term_lexical.value + 'a'}

    response = client.post(
        term_mchoice_router(exercise.id),
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == exercise.term_lexical.value


def test_check_term_mchoice_exercise_term_lexical_term_value_ref_correct(
    client, token_header
):
    term_value_ref = TermFactory()
    term_lexical = TermLexicalFactory(value=None, term_value_ref=term_value_ref)
    exercise = exercise_factory.TermMChoiceFactory(
        term=term_lexical.term,
        term_lexical=term_lexical,
    )
    payload = {'text': term_value_ref.expression}

    response = client.post(
        term_mchoice_router(exercise.id),
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == term_value_ref.expression


def test_check_term_mchoice_exercise_term_lexical_term_value_ref_incorrect(
    client, token_header
):
    term_value_ref = TermFactory()
    term_lexical = TermLexicalFactory(value=None, term_value_ref=term_value_ref)
    exercise = exercise_factory.TermMChoiceFactory(
        term=term_lexical.term,
        term_lexical=term_lexical,
    )
    payload = {'text': term_value_ref.expression + 'a'}

    response = client.post(
        term_mchoice_router(exercise.id),
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == term_value_ref.expression


def test_term_definition_mchoice_exercise(client, token_header):
    exercise = exercise_factory.TermDefinitionMChoiceFactory()

    response = client.get(
        term_definition_mchoice_router(exercise.id), headers=token_header
    )

    assert response.status_code == 200
    assert len(response.json()['choices']) == 4
    assert exercise.term_definition.definition in response.json()['choices']
    distractors = exercise.additional_content.get('distractors')
    choices = list(
        TermDefinition.objects.filter(id__in=distractors).values_list(
            'definition', flat=True
        )
    )
    assert any([choice in response.json()['choices'] for choice in choices])


def test_check_term_definition_mchoice_exercise_correct(client, token_header):
    exercise = exercise_factory.TermDefinitionMChoiceFactory()
    payload = {'text': exercise.term_definition.definition}

    response = client.post(
        term_definition_mchoice_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == exercise.term_definition.definition


def test_check_term_definition_mchoice_exercise_incorrect(client, token_header):
    exercise = exercise_factory.TermDefinitionMChoiceFactory()
    payload = {'text': exercise.term_definition.definition + 'a'}

    response = client.post(
        term_definition_mchoice_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == exercise.term_definition.definition


def test_term_image_mchoice_exercise(client, token_header):
    exercise = exercise_factory.TermImageMChoiceFactory()

    response = client.get(term_image_mchoice_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert len(response.json()['choices']) == 4
    assert response.json()['audio_file'] == exercise.term_pronunciation.audio_file
