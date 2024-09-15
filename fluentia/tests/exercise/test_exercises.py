# import pytest
# from django.db.models import OuterRef, Subquery
# from django.db.models.functions import Random
# from django.http.response import Http404

# from fluentia.apps.exercise import constants, exercises
# from fluentia.apps.exercise.exercises import _camel_to_snake
# from fluentia.apps.exercise.models import ExerciseHistory
# from fluentia.apps.term.constants import TermLexicalType
# from fluentia.apps.term.models import (
#     Term,
#     TermDefinition,
#     TermLexical,
#     TermPronunciation,
# )
# from fluentia.tests.factories import exercise as factory
# from fluentia.tests.factories.term import TermFactory, TermLexicalFactory

# pytestmark = pytest.mark.django_db


# def _convert_keys_to_int(dictionary):
#     if isinstance(dictionary, dict):
#         return {
#             int(k) if k.isdigit() else k: _convert_keys_to_int(v)
#             for k, v in dictionary.items()
#         }
#     return dictionary


# @pytest.mark.parametrize(
#     'input_text, expected_output',
#     [
#         ('OrderSentenceExercise', 'order_sentence_exercise'),
#         ('ListenTermExercise', 'listen_term_exercise'),
#         ('ListenTermMChoiceExercise', 'listen_term_mchoice_exercise'),
#         ('ListenSentenceExercise', 'listen_sentence_exercise'),
#         ('SpeakTermExercise', 'speak_term_exercise'),
#         ('SpeakSentenceExercise', 'speak_sentence_exercise'),
#         ('TermMChoiceExercise', 'term_mchoice_exercise'),
#         ('TermDefinitionMChoiceExercise', 'term_definition_mchoice_exercise'),
#         ('TermImageMChoiceExercise', 'term_image_mchoice_exercise'),
#         ('TermImageMChoiceTextExercise', 'term_image_mchoice_text_exercise'),
#         ('TermConnectionExercise', 'term_connection_exercise'),
#     ],
# )
# def test_camel_to_snake(input_text, expected_output):
#     assert _camel_to_snake(input_text) == expected_output


# exercise_parametrize = pytest.mark.parametrize(
#     'ExerciseClass, ExerciseFactory',
#     [
#         (exercises.OrderSentenceExercise, factory.OrderSentenceFactory),
#         (exercises.ListenTermExercise, factory.ListenTermFactory),
#         (exercises.ListenTermMChoiceExercise, factory.ListenTermMChoiceFactory),
#         (exercises.ListenSentenceExercise, factory.ListenSentenceFactory),
#         (exercises.SpeakTermExercise, factory.SpeakTermFactory),
#         (exercises.SpeakSentenceExercise, factory.SpeakSentenceFactory),
#         (exercises.TermMChoiceExercise, factory.TermMChoiceFactory),
#         (exercises.TermDefinitionMChoiceExercise, factory.TermDefinitionMChoiceFactory),
#         (exercises.TermImageMChoiceExercise, factory.TermImageMChoiceFactory),
#         (exercises.TermImageMChoiceTextExercise, factory.TermImageMChoiceTextFactory),
#         (exercises.TermConnectionExercise, factory.TermConnectionFactory),
#     ],
# )


# @exercise_parametrize
# def test_get_exercisel_model(ExerciseClass, ExerciseFactory):
#     exercise_db = ExerciseFactory()
#     exercise = ExerciseClass(exercise_db.id)

#     assert exercise.exercise == exercise_db


# @exercise_parametrize
# def test_get_exercise_model_not_found(ExerciseClass, ExerciseFactory):
#     with pytest.raises(Http404):
#         ExerciseClass(51903)


# class TestOrderSentenceExercise:
#     @pytest.fixture
#     def exercise(self):
#         exercise_db = factory.OrderSentenceFactory()
#         return exercises.OrderSentenceExercise(exercise_db.id)

#     def test_get_distractors(self, exercise):
#         distractors_dict = exercise.exercise.additional_content.get('distractors', {})
#         distractors_list = distractors_dict.get('term', [])
#         distractors_expression = Term.objects.filter(
#             id__in=distractors_list
#         ).values_list('expression', flat=True)
#         exercise_distractors_expression = exercise.get_distractors(min_distractors=1)
#         assert any(
#             [
#                 distractor in distractors_expression
#                 for distractor in exercise_distractors_expression
#             ]
#         )

#     def test_build(self, exercise):
#         build = exercise.build()

#         assert build['title'] == exercises.OrderSentenceExercise.title
#         assert build['description'] == exercises.OrderSentenceExercise.description
#         assert build['header'] == constants.ORDER_SENTENCE_HEADER
#         assert all(
#             [part in build['sentence'] for part in exercise.correct_answer.split()]
#         )

#     def test_correct_answer(self, exercise):
#         assert exercise.correct_answer == exercise.exercise.term_example.example

#     def test_assert_answer_correct(self, exercise):
#         assert exercise.assert_answer({'sentence': exercise.correct_answer})

#     def test_assert_answer_incorrect(self, exercise):
#         assert not exercise.assert_answer({'sentence': exercise.correct_answer + 'a'})

#     def test_check_correct(self, exercise, user):
#         exercise_request = exercise.build()
#         answer = {'sentence': exercise.correct_answer}
#         response = exercise.check(user, answer, exercise_request)

#         assert response == {
#             'correct': True,
#             'correct_answer': exercise.correct_answer,
#         }
#         history = ExerciseHistory.objects.filter(
#             user=user, exercise=exercise.exercise
#         ).first()
#         assert history is not None
#         assert history.correct is True
#         assert history.response == {
#             **answer,
#             'correct': True,
#             'correct_answer': exercise.correct_answer,
#         }
#         assert history.request == exercise_request

#     def test_check_incorrect(self, exercise, user):
#         exercise_request = exercise.build()
#         answer = {'sentence': exercise.correct_answer + 'a'}
#         response = exercise.check(user, answer, exercise_request)

#         assert response == {
#             'correct': False,
#             'correct_answer': exercise.correct_answer,
#         }
#         history = ExerciseHistory.objects.filter(
#             user=user, exercise=exercise.exercise
#         ).first()
#         assert history is not None
#         assert history.correct is False
#         assert history.response == {
#             **answer,
#             'correct': False,
#             'correct_answer': exercise.correct_answer,
#         }
#         assert history.request == exercise_request


# @pytest.mark.parametrize(
#     'get_exercise, get_answer',
#     [
#         (
#             lambda: exercises.ListenTermExercise(factory.ListenTermFactory().id),
#             lambda exercise: exercise.term.expression,
#         ),
#         (
#             lambda: exercises.ListenTermExercise(factory.ListenTermLexicalFactory().id),
#             lambda exercise: exercise.term_lexical.value,
#         ),
#         (
#             lambda: exercises.ListenTermExercise(
#                 factory.ListenTermLexicalFactory(
#                     term_lexical__value=None,
#                     term_lexical__term_value_ref=TermFactory(),
#                 ).id
#             ),
#             lambda exercise: exercise.term_lexical.term_value_ref.expression,
#         ),
#     ],
# )
# class TestListenTermExercise:
#     def test_build(self, get_exercise, get_answer):
#         exercise = get_exercise()
#         build = exercise.build()

#         assert build['title'] == exercises.ListenTermExercise.title
#         assert build['description'] == exercises.ListenTermExercise.description
#         assert build['header'] == constants.LISTEN_TERM_HEADER
#         assert build['audio_file'] == exercise.exercise.term_pronunciation.audio_file

#     def test_correct_answer(self, get_exercise, get_answer):
#         exercise = get_exercise()
#         answer = get_answer(exercise.exercise)

#         assert exercise.correct_answer == answer

#     def test_assert_answer_correct(self, get_exercise, get_answer):
#         exercise = get_exercise()
#         answer = get_answer(exercise.exercise)

#         assert exercise.assert_answer({'expression': answer})

#     def test_assert_answer_incorrect(self, get_exercise, get_answer):
#         exercise = get_exercise()
#         answer = get_answer(exercise.exercise)

#         assert not exercise.assert_answer({'expression': answer + 'a'})

#     def test_check_correct(self, get_exercise, get_answer, user):
#         exercise = get_exercise()
#         exercise_request = exercise.build()
#         answer = {'expression': get_answer(exercise.exercise)}
#         response = exercise.check(user, answer, exercise_request)

#         assert response == {
#             'correct': True,
#             'correct_answer': exercise.correct_answer,
#         }
#         history = ExerciseHistory.objects.filter(
#             user=user, exercise=exercise.exercise
#         ).first()
#         assert history is not None
#         assert history.correct is True
#         assert history.response == {
#             **answer,
#             'correct': True,
#             'correct_answer': exercise.correct_answer,
#         }
#         assert history.request == exercise_request

#     def test_check_incorrect(self, get_exercise, get_answer, user):
#         exercise = get_exercise()
#         exercise_request = exercise.build()
#         answer = {'expression': get_answer(exercise.exercise) + 'a'}
#         response = exercise.check(user, answer, exercise_request)

#         assert response == {
#             'correct': False,
#             'correct_answer': exercise.correct_answer,
#         }
#         history = ExerciseHistory.objects.filter(
#             user=user, exercise=exercise.exercise
#         ).first()
#         assert history is not None
#         assert history.correct is False
#         assert history.response == {
#             **answer,
#             'correct': False,
#             'correct_answer': exercise.correct_answer,
#         }
#         assert history.request == exercise_request


# class TestListenTermMChoiceExercise:
#     @pytest.fixture
#     def exercise(self):
#         exercise_db = factory.ListenTermMChoiceFactory()
#         return exercises.ListenTermMChoiceExercise(exercise_db.id)

#     def test_build(self, exercise):
#         build = exercise.build()

#         assert build['title'] == exercises.ListenTermMChoiceExercise.title
#         assert build['description'] == exercises.ListenTermMChoiceExercise.description
#         assert build['header'] == constants.LISTEN_MCHOICE_HEADER
#         assert len(build['choices']) == 4
#         assert exercise.correct_answer in build['choices']
#         assert (
#             build['choices'][exercise.correct_answer]['expression']
#             == exercise.exercise.term.expression
#         )
#         assert (
#             build['choices'][exercise.correct_answer]['audio_file']
#             == exercise.exercise.term_pronunciation.audio_file
#         )
#         distractor_choices = (
#             TermLexical.objects.filter(
#                 term_id=exercise.exercise.term_id,
#                 type=TermLexicalType.RHYME,
#                 term_value_ref__isnull=False,
#             )
#             .select_related('term_value_ref')
#             .annotate(random_order=Random())
#             .annotate(
#                 audio_file=Subquery(
#                     TermPronunciation.objects.filter(
#                         term_id=OuterRef('term_value_ref_id')
#                     ).values('audio_file')
#                 )
#             )
#             .order_by('random_order')
#             .values_list(
#                 'term_value_ref_id',
#                 'term_value_ref__expression',
#                 'audio_file',
#             )
#         )
#         assert (
#             sum(
#                 [
#                     expression == build['choices'].get(id_, {}).get('expression', '')
#                     and audio_file
#                     == build['choices'].get(id_, {}).get('audio_file', '')
#                     for id_, expression, audio_file in distractor_choices
#                 ]
#             )
#             == 3
#         )

#     def test_correct_answer(self, exercise):
#         assert exercise.correct_answer == exercise.exercise.term_id

#     def test_assert_answer_correct(self, exercise):
#         assert exercise.assert_answer({'term_id': exercise.correct_answer})

#     def test_assert_answer_incorrect(self, exercise):
#         assert not exercise.assert_answer({'term_id': exercise.correct_answer + 1})

#     def test_check_correct(self, exercise, user):
#         exercise_request = exercise.build()
#         answer = {'term_id': exercise.correct_answer}
#         response = exercise.check(user, answer, exercise_request)

#         assert response == {
#             'correct': True,
#             'correct_answer': exercise.correct_answer,
#         }
#         history = ExerciseHistory.objects.filter(
#             user=user, exercise=exercise.exercise
#         ).first()
#         assert history is not None
#         assert history.correct is True
#         assert history.response == {
#             **answer,
#             'correct': True,
#             'correct_answer': exercise.correct_answer,
#         }
#         assert _convert_keys_to_int(history.request) == exercise_request

#     def test_check_incorrect(self, exercise, user):
#         exercise_request = exercise.build()
#         answer = {'term_id': exercise.correct_answer + 1}
#         response = exercise.check(user, answer, exercise_request)

#         assert response == {
#             'correct': False,
#             'correct_answer': exercise.correct_answer,
#         }
#         history = ExerciseHistory.objects.filter(
#             user=user, exercise=exercise.exercise
#         ).first()
#         assert history is not None
#         assert history.correct is False
#         assert history.response == {
#             **answer,
#             'correct': False,
#             'correct_answer': exercise.correct_answer,
#         }
#         assert _convert_keys_to_int(history.request) == exercise_request


# class TestListenSentenceExercise:
#     @pytest.fixture
#     def exercise(self):
#         exercise_db = factory.ListenSentenceFactory()
#         return exercises.ListenSentenceExercise(exercise_db.id)

#     def test_build(self, exercise):
#         build = exercise.build()

#         assert build['title'] == exercises.ListenSentenceExercise.title
#         assert build['description'] == exercises.ListenSentenceExercise.description
#         assert build['header'] == constants.LISTEN_SENTENCE_HEADER
#         assert build['audio_file'] == exercise.exercise.term_pronunciation.audio_file

#     def test_correct_answer(self, exercise):
#         assert exercise.correct_answer == exercise.exercise.term_example.example

#     def test_assert_answer_correct(self, exercise):
#         assert exercise.assert_answer({'sentence': exercise.correct_answer})

#     def test_assert_answer_incorrect(self, exercise):
#         assert not exercise.assert_answer({'sentence': exercise.correct_answer + 'a'})

#     def test_check_correct(self, exercise, user):
#         exercise_request = exercise.build()
#         answer = {'sentence': exercise.correct_answer}
#         response = exercise.check(user, answer, exercise_request)

#         assert response == {
#             'correct': True,
#             'correct_answer': exercise.correct_answer,
#         }
#         history = ExerciseHistory.objects.filter(
#             user=user, exercise=exercise.exercise
#         ).first()
#         assert history is not None
#         assert history.correct is True
#         assert history.response == {
#             **answer,
#             'correct': True,
#             'correct_answer': exercise.correct_answer,
#         }
#         assert history.request == exercise_request

#     def test_check_incorrect(self, exercise, user):
#         exercise_request = exercise.build()
#         answer = {'sentence': exercise.correct_answer + 'a'}
#         response = exercise.check(user, answer, exercise_request)

#         assert response == {
#             'correct': False,
#             'correct_answer': exercise.correct_answer,
#         }
#         history = ExerciseHistory.objects.filter(
#             user=user, exercise=exercise.exercise
#         ).first()
#         assert history is not None
#         assert history.correct is False
#         assert history.response == {
#             **answer,
#             'correct': False,
#             'correct_answer': exercise.correct_answer,
#         }
#         assert history.request == exercise_request


# class TestSpeakTermExercise:
#     @pytest.fixture
#     def exercise(self):
#         exercise_db = factory.SpeakTermFactory()
#         return exercises.SpeakTermExercise(exercise_db.id)

#     def test_build(self, exercise):
#         build = exercise.build()

#         assert build['title'] == exercises.SpeakTermExercise.title
#         assert build['description'] == exercises.SpeakTermExercise.description
#         assert build['header'] == constants.SPEAK_TERM_HEADER.format(
#             term=exercise.correct_answer
#         )
#         assert build['audio_file'] == exercise.exercise.term_pronunciation.audio_file
#         assert build['phonetic'] == exercise.exercise.term_pronunciation.phonetic

#     def test_correct_answer(self, exercise):
#         assert exercise.correct_answer == exercise.exercise.term.expression

#     def test_assert_answer(self, exercise):
#         assert exercise.assert_answer({})  # TODO: SpeechToText API


# class TestSpeakSentenceExercise:
#     @pytest.fixture
#     def exercise(self):
#         exercise_db = factory.SpeakSentenceFactory()
#         return exercises.SpeakSentenceExercise(exercise_db.id)

#     def test_build(self, exercise):
#         build = exercise.build()

#         assert build['title'] == exercises.SpeakSentenceExercise.title
#         assert build['description'] == exercises.SpeakSentenceExercise.description
#         assert build['header'] == constants.SPEAK_SENTENCE_HEADER.format(
#             sentence=exercise.correct_answer
#         )
#         assert build['audio_file'] == exercise.exercise.term_pronunciation.audio_file
#         assert build['phonetic'] == exercise.exercise.term_pronunciation.phonetic

#     def test_correct_answer(self, exercise):
#         assert exercise.correct_answer == exercise.exercise.term_example.example

#     def test_assert_answer(self, exercise):
#         assert exercise.assert_answer({})  # TODO: SpeechToText API


# class TestTermMChoiceExercise:
#     parametrize_exercise = pytest.mark.parametrize(
#         'get_exercise, get_answer',
#         [
#             (
#                 lambda: exercises.TermMChoiceExercise(factory.TermMChoiceFactory().id),
#                 lambda exercise: exercise.exercise.term.id,
#             ),
#             (
#                 lambda: exercises.TermMChoiceExercise(
#                     factory.TermLexicalMChoiceFactory().id
#                 ),
#                 lambda exercise: exercise.exercise.term_lexical.id,
#             ),
#             (
#                 lambda: exercises.TermMChoiceExercise(
#                     factory.TermLexicalMChoiceFactory(

#                     ).id
#                 ),
#                 lambda exercise: exercise.exercise.term_lexical.id,
#             ),
#         ],
#     )

#     def test_get_distractors(self):
#         exercise = exercises.TermMChoiceExercise(factory.TermMChoiceFactory().id)
#         distractors_dict = exercise.exercise.additional_content.get('distractors', {})
#         distractors_list = distractors_dict.get('term', [])
#         distractors_query = Term.objects.filter(id__in=distractors_list).values_list(
#             'id', 'expression'
#         )
#         exercise_distractors = exercise.get_distractors()
#         assert (
#             sum(
#                 [
#                     id_ in exercise_distractors
#                     and value in exercise_distractors.values()
#                     for id_, value in distractors_query
#                 ]
#             )
#             == 3
#         )

#     def test_get_distractors_term_lexical_value(self):
#         exercise = exercises.TermMChoiceExercise(factory.TermLexicalMChoiceFactory().id)
#         distractors_dict = exercise.exercise.additional_content.get('distractors', {})
#         distractors_list = distractors_dict.get('term_lexical', [])
#         distractors_query = TermLexical.objects.filter(
#             id__in=distractors_list
#         ).values_list('id', 'value')
#         exercise_distractors = exercise.get_distractors()
#         assert (
#             sum(
#                 [
#                     id_ in exercise_distractors
#                     and value in exercise_distractors.values()
#                     for id_, value in distractors_query
#                 ]
#             )
#             == 3
#         )

#     def test_get_distractors_term_lexical_term_value_ref(self):
#         exercise = exercises.TermMChoiceExercise(
#             factory.TermLexicalMChoiceFactory(
#                 term_lexical__value=None,
#                 term_lexical__term_value_ref=TermFactory(),
#             ).id
#         )
#         distractors = [
#             TermLexicalFactory(
#                 value=None,
#                 term_value_ref=TermFactory(),
#             )
#             for _ in range(6)
#         ]
#         distractors_list = [distractor.id for distractor in distractors]
#         exercise.exercise.additional_content = {
#             'distractors': {'term_lexical': distractors_list}
#         }
#         distractors_query = TermLexical.objects.filter(
#             id__in=distractors_list
#         ).values_list('id', 'term_value_ref__expression')
#         exercise_distractors = exercise.get_distractors()
#         assert (
#             sum(
#                 [
#                     id_ in exercise_distractors
#                     and value in exercise_distractors.values()
#                     for id_, value in distractors_query
#                 ]
#             )
#             == 3
#         )

#     @pytest.mark.parametrize(
#         'get_exercise, get_answer',
#         [
#             (
#                 lambda: exercises.TermMChoiceExercise(factory.TermMChoiceFactory().id),
#                 lambda exercise: exercise.exercise.term.expression,
#             ),
#             (
#                 lambda: exercises.TermMChoiceExercise(
#                     factory.TermLexicalMChoiceFactory().id
#                 ),
#                 lambda exercise: exercise.exercise.term_lexical.value,
#             ),
#             (
#                 lambda: exercises.TermMChoiceExercise(
#                     factory.TermLexicalMChoiceFactory(
#                         term_lexical__value=None,
#                         term_lexical__term_value_ref=TermFactory(),
#                     ).id
#                 ),
#                 lambda exercise: exercise.exercise.term_lexical.term_value_ref.expression,
#             ),
#         ],
#     )
#     def test_build(self, get_exercise, get_answer):
#         exercise = get_exercise()
#         answer = get_answer(exercise)
#         build = exercise.build()

#         assert build['title'] == exercises.TermMChoiceExercise.title
#         assert build['description'] == exercises.TermMChoiceExercise.description
#         assert len(build['choices']) == 4
#         assert exercise.correct_answer in build['choices']
#         assert answer in build['choices'].values()

#     # TODO: TEST HIGHLIGHT TERM EXAMPLE HEADER

#     @parametrize_exercise
#     def test_correct_answer(self, get_exercise, get_answer):
#         exercise = get_exercise()
#         answer = get_answer(exercise)

#         assert exercise.correct_answer == answer

#     @parametrize_exercise
#     def test_assert_answer_correct(self, get_exercise, get_answer):
#         exercise = get_exercise()
#         answer = get_answer(exercise)

#         assert exercise.assert_answer({'term_id': answer})

#     @parametrize_exercise
#     def test_assert_answer_incorrect(self, get_exercise, get_answer):
#         exercise = get_exercise()
#         answer = get_answer(exercise) + 1

#         assert not exercise.assert_answer({'term_id': answer})

#     @parametrize_exercise
#     def test_check_correct(self, get_exercise, get_answer, user):
#         exercise = get_exercise()
#         answer = get_answer(exercise)
#         exercise_request = exercise.build()
#         answer = {'term_id': answer}
#         response = exercise.check(user, answer, exercise_request)

#         assert response == {
#             'correct': True,
#             'correct_answer': exercise.correct_answer,
#         }
#         history = ExerciseHistory.objects.filter(
#             user=user, exercise=exercise.exercise
#         ).first()
#         assert history is not None
#         assert history.correct is True
#         assert history.response == {
#             **answer,
#             'correct': True,
#             'correct_answer': exercise.correct_answer,
#         }
#         assert _convert_keys_to_int(history.request) == exercise_request

#     @parametrize_exercise
#     def test_check_incorrect(self, get_exercise, get_answer, user):
#         exercise = get_exercise()
#         answer = get_answer(exercise)
#         exercise_request = exercise.build()
#         answer = {'term_id': answer + 1}
#         response = exercise.check(user, answer, exercise_request)

#         assert response == {
#             'correct': False,
#             'correct_answer': exercise.correct_answer,
#         }
#         history = ExerciseHistory.objects.filter(
#             user=user, exercise=exercise.exercise
#         ).first()
#         assert history is not None
#         assert history.correct is False
#         assert history.response == {
#             **answer,
#             'correct': False,
#             'correct_answer': exercise.correct_answer,
#         }
#         assert _convert_keys_to_int(history.request) == exercise_request


# class TestTermDefinitionMChoiceExercise:
#     @pytest.fixture
#     def exercise(self):
#         exercise_db = factory.TermDefinitionMChoiceFactory()
#         return exercises.TermDefinitionMChoiceExercise(exercise_db.id)

#     def test_get_distractors(self, exercise):
#         distractors_list = exercise.exercise.additional_content.get('distractors')[
#             'term_definition'
#         ]
#         distractors_query = dict(
#             TermDefinition.objects.filter(id__in=distractors_list).values_list(
#                 'id', 'definition'
#             )
#         )
#         exercise_distractors = exercise.get_distractors()
#         assert (
#             sum(
#                 [
#                     id_ in exercise_distractors
#                     and definition in exercise_distractors.values()
#                     for id_, definition in distractors_query.items()
#                 ]
#             )
#             == 3
#         )

#     def test_build(self, exercise):
#         build = exercise.build()

#         assert build['title'] == exercises.TermDefinitionMChoiceExercise.title
#         assert (
#             build['description'] == exercises.TermDefinitionMChoiceExercise.description
#         )
#         assert build['header'] == constants.TERM_DEFINITION_MCHOICE_HEADER.format(
#             term=exercise.exercise.term.expression
#         )
#         assert len(build['choices']) == 4
#         assert exercise.correct_answer in build['choices']
#         assert exercise.exercise.term_definition.definition in build['choices'].values()

#     def test_correct_answer(self, exercise):
#         assert exercise.correct_answer == exercise.exercise.term_definition_id

#     def test_assert_answer_correct(self, exercise):
#         assert exercise.assert_answer({'term_definition_id': exercise.correct_answer})

#     def test_assert_answer_incorrect(self, exercise):
#         assert not exercise.assert_answer(
#             {'term_definition_id': exercise.correct_answer + 1}
#         )

#     def test_check_correct(self, exercise, user):
#         exercise_request = exercise.build()
#         answer = {'term_definition_id': exercise.correct_answer}
#         response = exercise.check(user, answer, exercise_request)

#         assert response == {
#             'correct': True,
#             'correct_answer': exercise.correct_answer,
#         }
#         history = ExerciseHistory.objects.filter(
#             user=user, exercise=exercise.exercise
#         ).first()
#         assert history is not None
#         assert history.correct is True
#         assert history.response == {
#             **answer,
#             'correct': True,
#             'correct_answer': exercise.correct_answer,
#         }
#         assert _convert_keys_to_int(history.request) == exercise_request

#     def test_check_incorrect(self, exercise, user):
#         exercise_request = exercise.build()
#         answer = {'term_definition_id': exercise.correct_answer + 1}
#         response = exercise.check(user, answer, exercise_request)

#         assert response == {
#             'correct': False,
#             'correct_answer': exercise.correct_answer,
#         }
#         history = ExerciseHistory.objects.filter(
#             user=user, exercise=exercise.exercise
#         ).first()
#         assert history is not None
#         assert history.correct is False
#         assert history.response == {
#             **answer,
#             'correct': False,
#             'correct_answer': exercise.correct_answer,
#         }
#         assert _convert_keys_to_int(history.request) == exercise_request
