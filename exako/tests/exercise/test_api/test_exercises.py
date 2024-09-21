import pytest
from django.urls import reverse_lazy

from exako.apps.exercise import constants, exercises
from exako.apps.exercise.models import ExerciseHistory
from exako.tests.factories import exercise as exercise_factory

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


def speak_term_router(exercise_id):
    return reverse_lazy(
        'api-1.0.0:speak_term_exercise', kwargs={'exercise_id': exercise_id}
    )


def speak_sentence_router(exercise_id):
    return reverse_lazy(
        'api-1.0.0:speak_sentence_exercise', kwargs={'exercise_id': exercise_id}
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


def term_image_mchoice_text_router(exercise_id):
    return reverse_lazy(
        'api-1.0.0:term_image_mchoice_text_exercise',
        kwargs={'exercise_id': exercise_id},
    )


def term_connection_router(exercise_id):
    return reverse_lazy(
        'api-1.0.0:term_connection_exercise',
        kwargs={'exercise_id': exercise_id},
    )


def test_order_sentence_exercise(client, token_header):
    exercise = exercise_factory.OrderSentenceFactory()

    response = client.get(order_sentence_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert response.json()['header'] == constants.ORDER_SENTENCE_HEADER
    assert response.json()['title'] == exercises.OrderSentenceExercise.title
    assert response.json()['description'] == exercises.OrderSentenceExercise.description
    assert all(
        [
            part in response.json()['sentence']
            for part in exercise.term_example.example.split()
        ]
    )


def test_check_order_sentence_exercise_correct(client, user, token_header):
    exercise = exercise_factory.OrderSentenceFactory()
    build = exercises.OrderSentenceExercise(exercise.id).build()
    payload = {
        'header': build['header'],
        'sentence': build['sentence'],
        'answer': {'sentence': exercise.term_example.example},
    }

    response = client.post(
        order_sentence_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == exercise.term_example.example
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


def test_check_order_sentence_exercise_incorrect(client, user, token_header):
    exercise = exercise_factory.OrderSentenceFactory()
    build = exercises.OrderSentenceExercise(exercise.id).build()
    payload = {
        'header': build['header'],
        'sentence': build['sentence'],
        'answer': {'sentence': exercise.term_example.example + 'a'},
    }

    response = client.post(
        order_sentence_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == exercise.term_example.example
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


@pytest.mark.parametrize(
    'get_exercise',
    [
        lambda: exercises.ListenTermExercise(exercise_factory.ListenTermFactory().id),
        lambda: exercises.ListenTermExercise(
            exercise_factory.ListenTermLexicalFactory().id
        ),
        lambda: exercises.ListenTermExercise(
            exercise_factory.ListenTermLexicalTermRefFactory().id
        ),
    ],
)
def test_listen_term_exercise(client, token_header, get_exercise):
    exercise = get_exercise()

    response = client.get(
        listen_term_router(exercise.exercise.id), headers=token_header
    )

    assert response.status_code == 200
    assert response.json()['header'] == constants.LISTEN_TERM_HEADER
    assert (
        response.json()['audio_file'] == exercise.exercise.term_pronunciation.audio_file
    )
    assert response.json()['title'] == exercises.ListenTermExercise.title
    assert response.json()['description'] == exercises.ListenTermExercise.description


@pytest.mark.parametrize(
    'get_exercise, get_answer',
    [
        (
            lambda: exercises.ListenTermExercise(
                exercise_factory.ListenTermFactory().id
            ),
            lambda exercise: exercise.term.expression,
        ),
        (
            lambda: exercises.ListenTermExercise(
                exercise_factory.ListenTermLexicalFactory().id
            ),
            lambda exercise: exercise.term_lexical.value,
        ),
        (
            lambda: exercises.ListenTermExercise(
                exercise_factory.ListenTermLexicalTermRefFactory().id
            ),
            lambda exercise: exercise.term_lexical.term_value_ref.expression,
        ),
    ],
)
def test_check_listen_term_exercise_correct(
    client, user, token_header, get_exercise, get_answer
):
    exercise = get_exercise()
    answer = get_answer(exercise.exercise)
    build = exercise.build()
    payload = {
        'header': build['header'],
        'audio_file': build['audio_file'],
        'answer': {'expression': answer},
    }

    response = client.post(
        listen_term_router(exercise.exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == answer
    history = ExerciseHistory.objects.filter(
        user=user, exercise=exercise.exercise
    ).first()
    assert history is not None


@pytest.mark.parametrize(
    'get_exercise, get_answer',
    [
        (
            lambda: exercises.ListenTermExercise(
                exercise_factory.ListenTermFactory().id
            ),
            lambda exercise: exercise.term.expression,
        ),
        (
            lambda: exercises.ListenTermExercise(
                exercise_factory.ListenTermLexicalFactory().id
            ),
            lambda exercise: exercise.term_lexical.value,
        ),
        (
            lambda: exercises.ListenTermExercise(
                exercise_factory.ListenTermLexicalTermRefFactory().id
            ),
            lambda exercise: exercise.term_lexical.term_value_ref.expression,
        ),
    ],
)
def test_check_listen_term_exercise_incorrect(
    client, user, token_header, get_exercise, get_answer
):
    exercise = get_exercise()
    answer = get_answer(exercise.exercise)
    build = exercises.ListenTermExercise(exercise.exercise.id).build()
    payload = {
        'header': build['header'],
        'audio_file': build['audio_file'],
        'answer': {'expression': answer + 'a'},
    }

    response = client.post(
        listen_term_router(exercise.exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == answer
    history = ExerciseHistory.objects.filter(
        user=user, exercise=exercise.exercise
    ).first()
    assert history is not None


def test_listen_term_mchoice_exercise(client, token_header):
    exercise = exercise_factory.ListenTermMChoiceFactory()

    response = client.get(listen_term_mchoice_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert response.json()['header'] == constants.LISTEN_MCHOICE_HEADER
    assert response.json()['title'] == exercises.ListenTermMChoiceExercise.title
    assert (
        response.json()['description']
        == exercises.ListenTermMChoiceExercise.description
    )
    assert len(response.json()['choices']) == 4
    assert str(exercise.term.id) in response.json()['choices']
    assert (
        response.json()['choices'][str(exercise.term.id)]['expression']
        == exercise.term.expression
    )
    assert (
        response.json()['choices'][str(exercise.term.id)]['audio_file']
        == exercise.term_pronunciation.audio_file
    )


def test_check_listen_term_mchoice_exercise_correct(client, user, token_header):
    exercise = exercise_factory.ListenTermMChoiceFactory()
    build = exercises.ListenTermMChoiceExercise(exercise.id).build()
    payload = {
        'header': build['header'],
        'choices': build['choices'],
        'answer': {'term_id': exercise.term.id},
    }

    response = client.post(
        listen_term_mchoice_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == exercise.term.id
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


def test_check_listen_term_mchoice_exercise_incorrect(client, user, token_header):
    exercise = exercise_factory.ListenTermMChoiceFactory()
    build = exercises.ListenTermMChoiceExercise(exercise.id).build()
    payload = {
        'header': build['header'],
        'choices': build['choices'],
        'answer': {'term_id': exercise.term.id + 1},
    }

    response = client.post(
        listen_term_mchoice_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == exercise.term.id
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


def test_listen_sentence_exercise(client, token_header):
    exercise = exercise_factory.ListenSentenceFactory()

    response = client.get(listen_sentence_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert response.json()['header'] == constants.LISTEN_SENTENCE_HEADER
    assert response.json()['title'] == exercises.ListenSentenceExercise.title
    assert (
        response.json()['description'] == exercises.ListenSentenceExercise.description
    )
    assert response.json()['audio_file'] == exercise.term_pronunciation.audio_file


def test_check_listen_sentence_exercise_correct(client, user, token_header):
    exercise = exercise_factory.ListenSentenceFactory()
    build = exercises.ListenSentenceExercise(exercise.id).build()
    payload = {
        'header': build['header'],
        'audio_file': build['audio_file'],
        'answer': {'sentence': exercise.term_example.example},
    }

    response = client.post(
        listen_sentence_router(exercise.id),
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == exercise.term_example.example
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


def test_check_listen_sentence_exercise_incorrect(client, user, token_header):
    exercise = exercise_factory.ListenSentenceFactory()
    build = exercises.ListenSentenceExercise(exercise.id).build()
    payload = {
        'header': build['header'],
        'audio_file': build['audio_file'],
        'answer': {'sentence': exercise.term_example.example + 'a'},
    }

    response = client.post(
        listen_sentence_router(exercise.id),
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == exercise.term_example.example
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


@pytest.mark.parametrize(
    'get_exercise, get_answer',
    [
        (
            lambda: exercises.TermMChoiceExercise(
                exercise_factory.TermMChoiceFactory().id
            ),
            lambda exercise: exercise.exercise.term.expression,
        ),
        (
            lambda: exercises.TermMChoiceExercise(
                exercise_factory.TermMChoiceLexicalFactory().id
            ),
            lambda exercise: exercise.exercise.term_lexical.value,
        ),
        (
            lambda: exercises.TermMChoiceExercise(
                exercise_factory.TermMChoiceLexicalTermRefFactory().id
            ),
            lambda exercise: exercise.exercise.term_lexical.term_value_ref.expression,
        ),
    ],
)
def test_term_mchoice_exercise_term(client, token_header, get_exercise, get_answer):
    exercise = get_exercise()
    answer = get_answer(exercise)

    response = client.get(
        term_mchoice_router(exercise.exercise.id), headers=token_header
    )

    assert response.status_code == 200
    assert response.json()['title'] == exercises.TermMChoiceExercise.title
    assert response.json()['description'] == exercises.TermMChoiceExercise.description
    assert len(response.json()['choices']) == 4
    assert str(exercise.correct_answer) in response.json()['choices']
    assert answer in response.json()['choices'].values()
    assert response.json()['header'] == constants.TERM_MCHOICE_HEADER.format(
        sentence=exercise._mask_sentence()
    )


@pytest.mark.parametrize(
    'get_exercise, get_answer',
    [
        (
            lambda: exercises.TermMChoiceExercise(
                exercise_factory.TermMChoiceFactory().id
            ),
            lambda exercise: exercise.exercise.term.id,
        ),
        (
            lambda: exercises.TermMChoiceExercise(
                exercise_factory.TermMChoiceLexicalFactory().id
            ),
            lambda exercise: exercise.exercise.term_lexical.id,
        ),
        (
            lambda: exercises.TermMChoiceExercise(
                exercise_factory.TermMChoiceLexicalTermRefFactory().id
            ),
            lambda exercise: exercise.exercise.term_lexical.id,
        ),
    ],
)
def test_check_term_mchoice_exercise_term_correct(
    client, user, token_header, get_exercise, get_answer
):
    exercise = get_exercise()
    answer = get_answer(exercise)
    build = exercise.build()
    payload = {
        'header': build['header'],
        'choices': build['choices'],
        'answer': {'term_id': answer},
    }

    response = client.post(
        term_mchoice_router(exercise.exercise.id),
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == answer
    history = ExerciseHistory.objects.filter(
        user=user, exercise=exercise.exercise
    ).first()
    assert history is not None


@pytest.mark.parametrize(
    'get_exercise, get_answer',
    [
        (
            lambda: exercises.TermMChoiceExercise(
                exercise_factory.TermMChoiceFactory().id
            ),
            lambda exercise: exercise.exercise.term.id,
        ),
        (
            lambda: exercises.TermMChoiceExercise(
                exercise_factory.TermMChoiceLexicalFactory().id
            ),
            lambda exercise: exercise.exercise.term_lexical.id,
        ),
        (
            lambda: exercises.TermMChoiceExercise(
                exercise_factory.TermMChoiceLexicalTermRefFactory().id
            ),
            lambda exercise: exercise.exercise.term_lexical.id,
        ),
    ],
)
def test_check_term_mchoice_exercise_term_incorrect(
    client, user, token_header, get_exercise, get_answer
):
    exercise = get_exercise()
    answer = get_answer(exercise)
    build = exercise.build()
    payload = {
        'header': build['header'],
        'choices': build['choices'],
        'answer': {'term_id': answer + 1},
    }

    response = client.post(
        term_mchoice_router(exercise.exercise.id),
        payload,
        content_type='application/json',
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == answer
    history = ExerciseHistory.objects.filter(
        user=user, exercise=exercise.exercise
    ).first()
    assert history is not None


def test_term_definition_mchoice_exercise(client, token_header):
    exercise = exercise_factory.TermDefinitionMChoiceFactory()

    response = client.get(
        term_definition_mchoice_router(exercise.id), headers=token_header
    )

    assert response.status_code == 200
    assert response.json()['title'] == exercises.TermDefinitionMChoiceExercise.title
    assert (
        response.json()['description']
        == exercises.TermDefinitionMChoiceExercise.description
    )
    assert response.json()['header'] == constants.TERM_DEFINITION_MCHOICE_HEADER.format(
        term=exercise.term.expression
    )
    assert len(response.json()['choices']) == 4
    assert str(exercise.term_definition.id) in response.json()['choices']
    assert exercise.term_definition.definition in response.json()['choices'].values()


def test_check_term_definition_mchoice_exercise_correct(client, user, token_header):
    exercise = exercise_factory.TermDefinitionMChoiceFactory()
    build = exercises.TermDefinitionMChoiceExercise(exercise.id).build()
    payload = {
        'header': build['header'],
        'choices': build['choices'],
        'answer': {'term_definition_id': exercise.term_definition.id},
    }

    response = client.post(
        term_definition_mchoice_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == exercise.term_definition.id
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


def test_check_term_definition_mchoice_exercise_incorrect(client, user, token_header):
    exercise = exercise_factory.TermDefinitionMChoiceFactory()
    build = exercises.TermDefinitionMChoiceExercise(exercise.id).build()
    payload = {
        'header': build['header'],
        'choices': build['choices'],
        'answer': {'term_definition_id': exercise.term_definition.id + 1},
    }

    response = client.post(
        term_definition_mchoice_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == exercise.term_definition.id
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


def test_term_image_mchoice_exercise(client, token_header):
    exercise = exercise_factory.TermImageMChoiceFactory()

    response = client.get(term_image_mchoice_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert response.json()['title'] == exercises.TermImageMChoiceExercise.title
    assert (
        response.json()['description'] == exercises.TermImageMChoiceExercise.description
    )
    assert response.json()['audio_file'] == exercise.term_pronunciation.audio_file
    assert response.json()['header'] == constants.TERM_IMAGE_MCHOICE_HEADER
    assert len(response.json()['choices']) == 4
    assert str(exercise.term.id) in response.json()['choices']
    assert exercise.term_image.image.url in response.json()['choices'].values()


def test_check_term_image_mchoice_exercise_correct(client, user, token_header):
    exercise = exercise_factory.TermImageMChoiceFactory()
    build = exercises.TermImageMChoiceExercise(exercise.id).build()
    payload = {
        'header': build['header'],
        'audio_file': build['audio_file'],
        'choices': build['choices'],
        'answer': {'term_id': exercise.term_id},
    }

    response = client.post(
        term_image_mchoice_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == exercise.term_id
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


def test_check_term_image_mchoice_exercise_incorrect(client, user, token_header):
    exercise = exercise_factory.TermImageMChoiceFactory()
    build = exercises.TermImageMChoiceExercise(exercise.id).build()
    payload = {
        'header': build['header'],
        'audio_file': build['audio_file'],
        'choices': build['choices'],
        'answer': {'term_id': exercise.term_id + 1},
    }

    response = client.post(
        term_image_mchoice_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == exercise.term_id
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


def test_term_image_mchoice_text_exercise(client, token_header):
    exercise = exercise_factory.TermImageMChoiceTextFactory()

    response = client.get(
        term_image_mchoice_text_router(exercise.id), headers=token_header
    )

    assert response.status_code == 200
    assert response.json()['title'] == exercises.TermImageMChoiceTextExercise.title
    assert (
        response.json()['description']
        == exercises.TermImageMChoiceTextExercise.description
    )
    assert response.json()['image'] == exercise.term_image.image.url
    assert response.json()['header'] == constants.TERM_IMAGE_MCHOICE_TEXT_HEADER
    assert len(response.json()['choices']) == 4
    assert str(exercise.term_id) in response.json()['choices']
    assert exercise.term.expression in response.json()['choices'].values()


def test_check_term_image_mchoice_text_exercise_correct(client, user, token_header):
    exercise = exercise_factory.TermImageMChoiceTextFactory()
    build = exercises.TermImageMChoiceTextExercise(exercise.id).build()
    payload = {
        'header': build['header'],
        'image': build['image'],
        'choices': build['choices'],
        'answer': {'term_id': exercise.term_id},
    }

    response = client.post(
        term_image_mchoice_text_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == exercise.term_id
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


def test_check_term_image_mchoice_text_exercise_incorrect(client, user, token_header):
    exercise = exercise_factory.TermImageMChoiceTextFactory()
    build = exercises.TermImageMChoiceTextExercise(exercise.id).build()
    payload = {
        'header': build['header'],
        'image': build['image'],
        'choices': build['choices'],
        'answer': {'term_id': exercise.term_id + 1},
    }

    response = client.post(
        term_image_mchoice_text_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == exercise.term_id
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


def test_term_connection_exercise(client, token_header):
    exercise = exercise_factory.TermConnectionFactory()

    response = client.get(term_connection_router(exercise.id), headers=token_header)

    assert response.status_code == 200
    assert response.json()['title'] == exercises.TermConnectionExercise.title
    assert (
        response.json()['description'] == exercises.TermConnectionExercise.description
    )
    assert response.json()['header'] == constants.TERM_CONNECTION_HEADER.format(
        term=exercise.term.expression
    )
    assert len(response.json()['choices']) == 12


def test_check_term_connection_exercise_correct(client, user, token_header):
    exercise = exercise_factory.TermConnectionFactory()
    exercise_class = exercises.TermConnectionExercise(exercise.id)
    build = exercise_class.build()
    payload = {
        'header': build['header'],
        'choices': build['choices'],
        'answer': {'choices': exercise.additional_content['connections']['term'][:4]},
    }

    response = client.post(
        term_connection_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is True
    assert response.json()['correct_answer'] == exercise_class.correct_answer
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


def test_check_term_connection_exercise_incorrect(client, user, token_header):
    exercise = exercise_factory.TermConnectionFactory()
    exercise_class = exercises.TermConnectionExercise(exercise.id)
    build = exercise_class.build()
    payload = {
        'header': build['header'],
        'choices': build['choices'],
        'answer': {'choices': exercise.additional_content['distractors']['term'][:4]},
    }

    response = client.post(
        term_connection_router(exercise.id),
        payload,
        headers=token_header,
        content_type='application/json',
    )

    assert response.status_code == 200
    assert response.json()['correct'] is False
    assert response.json()['correct_answer'] == exercise_class.correct_answer
    history = ExerciseHistory.objects.filter(user=user, exercise=exercise).first()
    assert history is not None


@pytest.mark.parametrize(
    'exercise_factory, router',
    [
        (exercise_factory.OrderSentenceFactory, order_sentence_router),
        (exercise_factory.ListenTermFactory, listen_term_router),
        (exercise_factory.ListenTermLexicalFactory, listen_term_router),
        (exercise_factory.ListenTermLexicalTermRefFactory, listen_term_router),
        (exercise_factory.ListenSentenceFactory, listen_sentence_router),
        (exercise_factory.ListenTermMChoiceFactory, listen_term_mchoice_router),
        (exercise_factory.SpeakTermFactory, speak_term_router),
        (exercise_factory.SpeakTermLexicalFactory, speak_term_router),
        (exercise_factory.SpeakTermLexicalTermRefFactory, speak_term_router),
        (exercise_factory.SpeakSentenceFactory, speak_sentence_router),
        (exercise_factory.TermMChoiceFactory, term_mchoice_router),
        (exercise_factory.TermMChoiceLexicalFactory, term_mchoice_router),
        (exercise_factory.TermMChoiceLexicalTermRefFactory, term_mchoice_router),
        (exercise_factory.TermDefinitionMChoiceFactory, term_definition_mchoice_router),
        (exercise_factory.TermImageMChoiceFactory, term_image_mchoice_router),
        (exercise_factory.TermImageMChoiceTextFactory, term_image_mchoice_text_router),
        (exercise_factory.TermConnectionFactory, term_connection_router),
    ],
)
def test_get_exercise_user_not_authenticated(client, exercise_factory, router):
    exercise = exercise_factory()

    response = client.get(router(exercise.id))

    assert response.status_code == 401


@pytest.mark.parametrize(
    'exercise_factory, router',
    [
        (exercise_factory.OrderSentenceFactory, listen_term_mchoice_router),
        (exercise_factory.ListenTermFactory, speak_sentence_router),
        (exercise_factory.ListenTermLexicalFactory, term_mchoice_router),
        (exercise_factory.ListenTermLexicalTermRefFactory, term_image_mchoice_router),
        (exercise_factory.ListenSentenceFactory, term_connection_router),
        (exercise_factory.ListenTermMChoiceFactory, listen_term_router),
        (exercise_factory.SpeakTermFactory, term_definition_mchoice_router),
        (exercise_factory.SpeakTermLexicalFactory, term_image_mchoice_text_router),
        (exercise_factory.SpeakTermLexicalTermRefFactory, listen_sentence_router),
        (exercise_factory.SpeakSentenceFactory, term_mchoice_router),
        (exercise_factory.TermMChoiceFactory, speak_term_router),
        (exercise_factory.TermMChoiceLexicalFactory, order_sentence_router),
        (exercise_factory.TermMChoiceLexicalTermRefFactory, listen_term_router),
        (exercise_factory.TermDefinitionMChoiceFactory, speak_term_router),
        (exercise_factory.TermImageMChoiceFactory, term_mchoice_router),
        (exercise_factory.TermImageMChoiceTextFactory, listen_term_router),
        (exercise_factory.TermConnectionFactory, speak_term_router),
    ],
)
def test_get_exercise_does_not_exists(client, token_header, exercise_factory, router):
    exercise = exercise_factory()

    response = client.get(router(exercise.id), headers=token_header)

    assert response.status_code


@pytest.mark.parametrize(
    'exercise_factory, router',
    [
        (exercise_factory.OrderSentenceFactory, order_sentence_router),
        (exercise_factory.ListenTermFactory, listen_term_router),
        (exercise_factory.ListenTermLexicalFactory, listen_term_router),
        (exercise_factory.ListenTermLexicalTermRefFactory, listen_term_router),
        (exercise_factory.ListenSentenceFactory, listen_sentence_router),
        (exercise_factory.ListenTermMChoiceFactory, listen_term_mchoice_router),
        (exercise_factory.SpeakTermFactory, speak_term_router),
        (exercise_factory.SpeakTermLexicalFactory, speak_term_router),
        (exercise_factory.SpeakTermLexicalTermRefFactory, speak_term_router),
        (exercise_factory.SpeakSentenceFactory, speak_sentence_router),
        (exercise_factory.TermMChoiceFactory, term_mchoice_router),
        (exercise_factory.TermMChoiceLexicalFactory, term_mchoice_router),
        (exercise_factory.TermMChoiceLexicalTermRefFactory, term_mchoice_router),
        (exercise_factory.TermDefinitionMChoiceFactory, term_definition_mchoice_router),
        (exercise_factory.TermImageMChoiceFactory, term_image_mchoice_router),
        (exercise_factory.TermImageMChoiceTextFactory, term_image_mchoice_text_router),
        (exercise_factory.TermConnectionFactory, term_connection_router),
    ],
)
def test_check_exercise_user_not_authenticated(client, exercise_factory, router):
    exercise = exercise_factory()

    response = client.post(router(exercise.id))

    assert response.status_code == 401


@pytest.mark.parametrize(
    'exercise_factory, router',
    [
        (exercise_factory.OrderSentenceFactory, listen_term_mchoice_router),
        (exercise_factory.ListenTermFactory, speak_sentence_router),
        (exercise_factory.ListenTermLexicalFactory, term_mchoice_router),
        (exercise_factory.ListenTermLexicalTermRefFactory, term_image_mchoice_router),
        (exercise_factory.ListenSentenceFactory, term_connection_router),
        (exercise_factory.ListenTermMChoiceFactory, listen_term_router),
        (exercise_factory.SpeakTermFactory, term_definition_mchoice_router),
        (exercise_factory.SpeakTermLexicalFactory, term_image_mchoice_text_router),
        (exercise_factory.SpeakTermLexicalTermRefFactory, listen_sentence_router),
        (exercise_factory.SpeakSentenceFactory, term_mchoice_router),
        (exercise_factory.TermMChoiceFactory, speak_term_router),
        (exercise_factory.TermMChoiceLexicalFactory, order_sentence_router),
        (exercise_factory.TermMChoiceLexicalTermRefFactory, listen_term_router),
        (exercise_factory.TermDefinitionMChoiceFactory, speak_term_router),
        (exercise_factory.TermImageMChoiceFactory, term_mchoice_router),
        (exercise_factory.TermImageMChoiceTextFactory, listen_term_router),
        (exercise_factory.TermConnectionFactory, speak_term_router),
    ],
)
def test_check_exercise_does_not_exists(client, token_header, exercise_factory, router):
    exercise = exercise_factory()

    response = client.post(router(exercise.id), headers=token_header)

    assert response.status_code
