from random import random, sample, shuffle

from django.db import IntegrityError, models
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Random
from django.shortcuts import get_object_or_404
from ninja import File, Query, Router, UploadedFile
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from fluentia.apps.card.models import Card
from fluentia.apps.core import schema as core_schema
from fluentia.apps.core.permissions import is_admin, permission_required
from fluentia.apps.exercise import constants
from fluentia.apps.exercise.api import schema
from fluentia.apps.exercise.constants import ExerciseType
from fluentia.apps.exercise.models import Exercise, ExerciseLevel, RandomSeed
from fluentia.apps.term.constants import Language, Level, TermLexicalType
from fluentia.apps.term.models import (
    Term,
    TermDefinition,
    TermExample,
    TermLexical,
    TermPronunciation,
)
from fluentia.apps.user.auth.token import AuthBearer

exercise_router = Router(tags=['Exercício'], auth=AuthBearer())


@exercise_router.post(
    path='/',
    response={
        201: schema.ExerciseSchemaView,
        401: core_schema.NotAuthenticated,
        403: core_schema.PermissionDenied,
        404: core_schema.NotFound,
    },
    summary='Criar um novo exercício.',
    description='Endpoint criado para criar um novo tipo de exercício baseado em um termo existente.',
    openapi_extra={
        'responses': {
            409: {
                'description': 'O exercício específicado já existe.',
                'content': {
                    'application/json': {
                        'example': {'detail': 'exercise already exists.'}
                    }
                },
            },
        }
    },
)
@permission_required([is_admin])
def create_exercise(request, exercise_schema: schema.ExerciseSchema):
    try:
        return 201, Exercise.objects.create(**exercise_schema.model_dump())
    except IntegrityError:
        raise HttpError(status_code=409, message='exercise already exists.')


@exercise_router.get(
    path='/',
    response={200: list[schema.ExerciseView]},
    summary='Consulta exercícios sobre termos disponíveis.',
    description='Endpoint para retornar exercícios sobre termos. Os exercícios serão montados com termos aleatórios, a menos que seja específicado o cardset_id.',
)
@paginate(PageNumberPagination)
def list_exercise(
    request,
    language: Language,
    exercise_type: ExerciseType | None = Query(default=ExerciseType.RANDOM),
    level: Level | None = Query(
        default=None, description='Filtar por dificuldade do termo.'
    ),
    cardset_id: int | None = Query(
        default=None, description='Filtrar por conjunto de cartas.'
    ),
    seed: float | None = Query(default_factory=random, le=1, ge=0),
):
    queryset = (
        Exercise.objects.filter(language=language)
        .annotate(
            md5_seed=RandomSeed(
                models.F('id'),
                seed=seed,
                output_field=models.CharField(),
            )
        )
        .order_by('md5_seed')
    )

    if exercise_type != ExerciseType.RANDOM:
        queryset = queryset.filter(type=exercise_type)

    if cardset_id:
        cardset_query = Card.objects.filter(
            cardset__user=request.user, cardset_id=cardset_id
        ).values('term')
        queryset = queryset.filter(models.Q(term__in=cardset_query))

    if level:
        level_query = ExerciseLevel.objects.filter(level=level).values('exercise_id')
        queryset = queryset.filter(id__in=level_query)
    return queryset.values('type', 'id')


@exercise_router.get(
    path='/order-sentence/{exercise_id}',
    response={
        200: schema.OrderSentenceView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Exercício sobre reodernar frases.',
    description="""
    Endpoint que retorna uma frase embaralhada relacionada a um termo e o usuário terá que reordenar a frase na ordem correta.
    """,
)
def order_sentence_exercise(request, exercise_id: int):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        type=ExerciseType.ORDER_SENTENCE,
    )
    sentence = (
        TermExample.objects.filter(id=exercise.term_example_id)
        .values_list('example')
        .first()
    )
    print(sentence)
    sentence_parts = sentence.split()
    distractors_parts = Term.objects.filter(
        id__in=exercise.additional_content.get('distractors', [])
    ).values_list('expression', flat=True)
    sentence_parts += distractors_parts
    return schema.OrderSentenceView(
        header=constants.ORDER_SENTENCE_HEADER,
        sentence=shuffle(sentence_parts),
    )


@exercise_router.post(
    path='/order-sentence/{exercise_id}',
    response=schema.ExerciseResponse,
)
def check_order_sentence_exercise(
    request,
    exercise_id: int,
    exercise_schema: schema.OrderSentenceCheck,
):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        type=ExerciseType.ORDER_SENTENCE,
    )
    sentence = (
        TermExample.objects.filter(id=exercise.term_example_id)
        .values('example')
        .first()
    )
    correct = sentence.split() == exercise_schema.sentence
    return schema.ExerciseResponse(correct=correct, correct_answer=sentence)


@exercise_router.get(
    path='/listen-term/{exercise_id}',
    response={
        200: schema.ListenView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Exercício sobre escuta de pronúncia de termos.',
    description='Endpoint que retorna a pronúncia em forma de aúdio de um texto para o usuário responder qual o termo correspondente.',
)
def listen_term_exercise(request, exercise_id: int):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        type=ExerciseType.LISTEN_TERM,
    )
    audio_file = (
        TermPronunciation.objects.filter(id=exercise.term_pronunciation_id)
        .values('audio_file')
        .first()
    )
    return schema.ListenView(
        header=constants.LISTEN_TERM_HEADER,
        audio_file=audio_file,
    )


@exercise_router.post(
    path='/listen-term/{exercise_id}',
    response=schema.ExerciseResponse,
)
def check_listen_term_exercise(
    request, exercise_id: int, exercise_schema: schema.TextCheck
):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        type=ExerciseType.LISTEN_TERM,
    )
    if exercise.term_lexical_id:
        value, expression = (
            TermLexical.objects.filter(id=exercise.term_lexical_id)
            .values('value', 'term_value_ref__expression')
            .first()
        )
        text = value or expression
    else:
        text = Term.objects.filter(id=exercise.term_id).values('expression').first()
    correct = text.lower() == exercise_schema.text.lower()
    return schema.ExerciseResponse(correct=correct, correct_answert=text)


@exercise_router.get(
    path='/listen-term-mchoice/{exercise_id}',
    response={
        200: schema.ListenMChoiceView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Exercício sobre escuta de pronúncia de termos.',
    description='Endpoint que retorna a pronúncia de um termo em forma de aúdio de um texto para o usuário responder qual o termo correspondente a partir das alternativas disponíveis com palavras similares.',
)
def listen_term_mchoice_exercise(request, exercise_id: int):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        type=ExerciseType.LISTEN_TERM_MCHOICE,
    )

    choices = (
        TermLexical.objects.filter(
            term_id=exercise.term_id,
            type=TermLexicalType.RHYME,
            term_value_ref__is_null=False,
        )
        .select_related('term_value_ref')
        .annotate(random_order=Random())
        .annotate(
            audio_file=Subquery(
                TermPronunciation.objects.filter(
                    term_id=OuterRef('term_value_ref_id')
                ).values('audio_file')
            )
        )
        .order_by('random_order')[:3]
        .values(
            'term_value_ref__expression',
            'audio_file',
        )
    )
    alternatives = {expression: audio_file for expression, audio_file in choices}

    expression = Term.objects.filter(id=exercise.term_id).values('expression').first()
    audio_file = (
        TermPronunciation.objects.filter(id=exercise.term_pronunciation_id)
        .values('audio_file')
        .first()
    )
    alternatives[expression] = audio_file

    return schema.ListenMChoiceView(
        header=constants.LISTEN_MCHOICE_HEADER,
        choices=alternatives,
    )


@exercise_router.post(
    path='/listen-term-mchoice/{exercise_id}',
    response=schema.ExerciseResponse,
)
def check_listen_term_mchoice_exercise(
    request, exercise_id: int, exercise_schema: schema.TextCheck
):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        type=ExerciseType.LISTEN_TERM_MCHOICE,
    )

    text = Term.objects.filter(id=exercise.term_id).values('expression').first()
    correct = text.lower() == exercise_schema.text.lower()
    return schema.ExerciseResponse(correct=correct, correct_answert=text)


@exercise_router.get(
    path='/listen-sentence/{exercise_id}',
    response={
        200: schema.ListenView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Exercício sobre escuta de pronúncia de frase.',
    description='Endpoint que retorna a pronúncia em forma de aúdio de uma frase relacionada ao termo para o usuário escrever a frase corretamente.',
)
def listen_sentence_exercise(request, exercise_id: int):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        type=ExerciseType.LISTEN_SENTENCE,
    )
    audio_file = (
        TermPronunciation.objects.filter(id=exercise.term_pronunciation_id)
        .values('audio_file')
        .first()
    )
    return schema.ListenView(
        header=constants.LISTEN_SENTENCE_HEADER,
        audio_file=audio_file,
    )


@exercise_router.post(
    path='/listen-sentence/{exercise_id}',
    response=schema.ExerciseResponse,
)
def check_listen_sentence_exercise(
    request, exercise_id: int, exercise_schema: schema.TextCheck
):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        type=ExerciseType.LISTEN_SENTENCE,
    )
    text = (
        TermExample.objects.filter(id=exercise.term_example_id)
        .values('example')
        .first()
    )
    correct = text.lower() == exercise_schema.text.lower()
    return schema.ExerciseResponse(correct=correct, correct_answert=text)


@exercise_router.get(
    path='/speak-term/{exercise_id}',
    response={
        200: schema.SpeakView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Exercício sobre pronúnciação de termos.',
    description='Endpoint que retorna um link para enviar a pronúncia em forma de aúdio de um usuário sobre um termo.',
)
def speak_term_exercise(request, exercise_id: int):
    pass


@exercise_router.post(
    path='/speak-term/{exercise_id}',
    response=schema.ExerciseResponse,
)
def check_speak_term_exercise(
    request, exercise_id: int, audio: UploadedFile = File(...)
):
    pass


@exercise_router.get(
    path='/speak-sentence/{exercise_id}',
    response={
        200: schema.SpeakView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Exercício sobre pronúnciação de termos.',
    description='Endpoint que retorna um link para enviar a pronúncia em forma de aúdio de um usuário sobre um termo.',
)
def speak_sentence_exercise(request, exercise_id: int):
    pass


@exercise_router.post(
    path='/speak-sentence/{exercise_id}',
    response=schema.ExerciseResponse,
)
def check_speak_sentence_exercise(request, exercise_id: int):
    pass


@exercise_router.get(
    path='/mchoice-term/{exercise_id}',
    response={
        200: schema.MultipleChoiceView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Exercício de multipla escolha sobre termos.',
    description='Endpoint que retorará uma frase com um termo atrelado faltando, no qual será necessário escolher entre as opções qual completa o espaço na frase.',
)
def term_mchoice_exercise(request, exercise_id: int):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        type=ExerciseType.TERM_MCHOICE,
    )
    if exercise.term_lexical_id:
        value, expression = (
            TermLexical.objects.filter(id=exercise.term_lexical_id)
            .values('value', 'term_value_ref__expression')
            .first()
        )
        text = value or expression
    else:
        text = Term.objects.filter(id=exercise.term_id).values('expression').first()
    distractors = exercise.additional_content.get('distractors')
    term_ids = list(sample(distractors, 3))
    alternatives = Term.objects.filter(id__in=term_ids).values('expression')
    alternatives.append(text)
    return schema.MultipleChoiceView(
        header=constants.MCHOICE_TERM_HEADER,
        choices=alternatives,
    )


@exercise_router.post(
    path='/mchoice-term/{exercise_id}',
    response=schema.TextCheck,
)
def check_term_mchoice_exercise(
    request, exercise_id: int, exercise_schema: schema.TextCheck
):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        type=ExerciseType.LISTEN_TERM,
    )
    if exercise.term_lexical_id:
        value, expression = (
            TermLexical.objects.filter(id=exercise.term_lexical_id)
            .values('value', 'term_value_ref__expression')
            .first()
        )
        text = value or expression
    else:
        text = Term.objects.filter(id=exercise.term_id).values('expression').first()
    correct = text.lower() == exercise_schema.text.lower()
    return schema.ExerciseResponse(correct=correct, correct_answert=text)


@exercise_router.get(
    path='/mchoice-definition/{exercise_id}',
    response={
        200: schema.MultipleChoiceView,
        401: core_schema.NotAuthenticated,
        404: core_schema.NotFound,
    },
    summary='Exercício de multipla escolha sobre definições de termos.',
    description='O usuário receberá um termo, no qual será necessário escolher entre as opções qual pertence ao termo.',
)
def term_definition_mchoice_exercise(request, exercise_id: int):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        type=ExerciseType.TERM_DEFINITION_MCHOICE,
    )
    distractors = exercise.additional_content.get('distractors')
    definition_ids = list(sample(distractors, 3))
    alternatives = list(
        TermDefinition.objects.filter(id__in=definition_ids).values('definition')
    )
    definition = (
        TermDefinition.objects.filter(id=exercise.term_definition_id)
        .values('definition')
        .first()
    )
    alternatives.append(definition)

    term = Term.objects.filter(id=exercise.term_id).values('expression').first()
    return schema.MultipleChoiceView(
        header=constants.MCHOICE_TERM_DEFINITION_HEADER.format(term=term),
        choices=alternatives,
    )


@exercise_router.post(
    path='/mchoice-definition/{exercise_id}',
    response=schema.ExerciseResponse,
)
def check_term_definition_mchoice_exercise(
    request,
    exercise_id: int,
    exercise_schema: schema.ExerciseSchema,
):
    exercise = get_object_or_404(
        Exercise,
        id=exercise_id,
        type=ExerciseType.TERM_DEFINITION_MCHOICE,
    )
    text = Term.objects.filter(id=exercise.term_id).values('expression').first()
    correct = text.lower() == exercise_schema.text.lower()
    return schema.ExerciseResponse(correct=correct, correct_answert=text)
