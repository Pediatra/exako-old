from random import random

from django.db import IntegrityError
from ninja import Field, Query, Router
from ninja.errors import HttpError
from ninja.pagination import PageNumberPagination, paginate

from exako.apps.core import schema as core_schema
from exako.apps.core.permissions import is_admin, permission_required
from exako.apps.exercise import exercises
from exako.apps.exercise.api import schema
from exako.apps.exercise.constants import ExerciseSubType, ExerciseType
from exako.apps.exercise.models import Exercise
from exako.apps.term.constants import Language, Level
from exako.apps.user.auth.token import AuthBearer

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
        },
        'requestBody': {
            'content': {
                'application/json': {
                    'examples': {
                        'exercise1': {
                            'summary': 'OrderSentenceSchema',
                            'value': schema.OrderSentenceSchema(
                                language=Language.PORTUGUESE_BRASILIAN,
                                type=ExerciseType.ORDER_SENTENCE,
                                term_example=1,
                                additional_content={
                                    'distractors': {'term': [1, 2, 3, 4]}
                                },
                            ),
                        },
                        'exercise2': {
                            'summary': 'ListenTermSchema',
                            'value': schema.ListenTermSchema(
                                language=Language.PORTUGUESE_BRASILIAN,
                                type=ExerciseType.LISTEN_TERM,
                                term_pronunciation=1,
                                term=1,
                                additional_content={'sub_type': ExerciseSubType.TERM},
                            ),
                        },
                        'exercises3': {
                            'summary': 'ListenSentenceSchema',
                            'value': schema.ListenSentenceSchema(
                                language=Language.PORTUGUESE_BRASILIAN,
                                type=ExerciseType.LISTEN_SENTENCE,
                                term_pronunciation=1,
                                term_example=1,
                            ),
                        },
                        'exercises4': {
                            'summary': 'ListenTermMChoiceSchema',
                            'value': schema.ListenTermMChoiceSchema(
                                language=Language.PORTUGUESE_BRASILIAN,
                                type=ExerciseType.LISTEN_TERM_MCHOICE,
                                term_pronunciation=1,
                                term=1,
                            ),
                        },
                        'exercises5': {
                            'summary': 'SpeakTermSchema',
                            'value': schema.SpeakTermSchema(
                                language=Language.PORTUGUESE_BRASILIAN,
                                type=ExerciseType.SPEAK_TERM,
                                term_pronunciation=1,
                                term=1,
                                additional_content={'sub_type': ExerciseSubType.TERM},
                            ),
                        },
                        'exercises6': {
                            'summary': 'SpeakSentenceSchema',
                            'value': schema.SpeakSentenceSchema(
                                language=Language.PORTUGUESE_BRASILIAN,
                                type=ExerciseType.SPEAK_SENTENCE,
                                term_pronunciation=1,
                                term_example=1,
                            ),
                        },
                        'exercises7': {
                            'summary': 'TermMChoiceSchema',
                            'value': schema.TermMChoiceSchema(
                                language=Language.PORTUGUESE_BRASILIAN,
                                type=ExerciseType.TERM_MCHOICE,
                                term=1,
                                term_example=1,
                                additional_content={
                                    'distractors': {
                                        'term': [1, 3, 5, 7],
                                        'term_lexical': [1, 5, 6, 8],
                                    },
                                    'sub_type': ExerciseSubType.TERM,
                                },
                            ),
                        },
                        'exercises8': {
                            'summary': 'TermDefinitionMChoiceSchema',
                            'value': schema.TermDefinitionMChoiceSchema(
                                language=Language.PORTUGUESE_BRASILIAN,
                                type=ExerciseType.TERM_DEFINITION_MCHOICE,
                                term=1,
                                term_definition=1,
                                additional_content={
                                    'distractors': {'term_definition': [1, 3, 5, 7]}
                                },
                            ),
                        },
                        'exercises9': {
                            'summary': 'TermImageMChoiceSchema',
                            'value': schema.TermImageMChoiceSchema(
                                language=Language.PORTUGUESE_BRASILIAN,
                                type=ExerciseType.TERM_IMAGE_MCHOICE,
                                term=1,
                                term_image=1,
                                term_pronunciation=1,
                                additional_content={
                                    'distractors': {'term_image': [1, 3, 5, 7]}
                                },
                            ),
                        },
                        'exercises10': {
                            'summary': 'TermImageMChoiceTextSchema',
                            'value': schema.TermImageMChoiceTextSchema(
                                language=Language.PORTUGUESE_BRASILIAN,
                                type=ExerciseType.TERM_IMAGE_MCHOICE_TEXT,
                                term=1,
                                term_image=1,
                                additional_content={
                                    'distractors': {'term': [1, 3, 5, 7]}
                                },
                            ),
                        },
                        'exercises11': {
                            'summary': 'TermConnectionSchema',
                            'value': schema.TermConnectionSchema(
                                language=Language.PORTUGUESE_BRASILIAN,
                                type=ExerciseType.TERM_CONNECTION,
                                term=1,
                                additional_content={
                                    'distractors': {'term': [1, 3, 5, 7, 8, 9, 11, 12]},
                                    'connections': {'term': [1, 5, 7, 9]},
                                },
                            ),
                        },
                    },
                }
            }
        },
    },
)
@permission_required([is_admin])
def create_exercise(request, ExerciseSchema: schema.ExerciseSchema):
    try:
        return 201, Exercise.objects.create(**ExerciseSchema.model_dump())
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
    language: list[Language] = Query(...),
    exercise_type: list[ExerciseType] | None = Query(default=ExerciseType.RANDOM),
    level: list[Level] | None = Query(
        default=None, description='Filtar por dificuldade do termo.'
    ),
    cardset_id: list[int] | None = Query(
        default=None, description='Filtrar por conjunto de cartas.'
    ),
    seed: float | None = Query(default_factory=random, le=1, ge=0),
):
    return Exercise.objects.list(
        language=language,
        exercise_type=exercise_type,
        level=level,
        cardset_id=cardset_id,
        seed=seed,
        user=request.user,
    )


exercises.OrderSentenceExercise.as_endpoint(
    router=exercise_router,
    path='/order-sentence/{exercise_id}',
    ExerciseSchema=schema.OrderSentenceView,
    sentence=str,
)

exercises.ListenTermExercise.as_endpoint(
    router=exercise_router,
    path='/listen-term/{exercise_id}',
    ExerciseSchema=schema.ListenView,
    expression=str,
)

exercises.ListenTermMChoiceExercise.as_endpoint(
    router=exercise_router,
    path='/listen-term-mchoice/{exercise_id}',
    ExerciseSchema=schema.ListenMChoiceView,
    term_id=int,
)

exercises.ListenSentenceExercise.as_endpoint(
    router=exercise_router,
    path='/listen-sentence/{exercise_id}',
    ExerciseSchema=schema.ListenView,
    sentence=str,
)

exercises.SpeakTermExercise.as_endpoint(
    router=exercise_router,
    path='/speak-term/{exercise_id}',
    ExerciseSchema=schema.SpeakView,
)

exercises.SpeakSentenceExercise.as_endpoint(
    router=exercise_router,
    path='/speak-sentence/{exercise_id}',
    ExerciseSchema=schema.SpeakView,
)

exercises.TermMChoiceExercise.as_endpoint(
    router=exercise_router,
    path='/term-mchoice/{exercise_id}',
    ExerciseSchema=schema.TermMChoiceView,
    term_id=int,
)

exercises.TermDefinitionMChoiceExercise.as_endpoint(
    router=exercise_router,
    path='/definition-mchoice/{exercise_id}',
    ExerciseSchema=schema.TermMChoiceView,
    term_definition_id=int,
)

exercises.TermImageMChoiceExercise.as_endpoint(
    router=exercise_router,
    path='/term-image-mchoice/{exercise_id}',
    ExerciseSchema=schema.ImageMChoiceView,
    term_id=int,
)

exercises.TermImageMChoiceTextExercise.as_endpoint(
    router=exercise_router,
    path='/term-image-text-mchoice/{exercise_id}',
    ExerciseSchema=schema.TextImageMChoiceView,
    term_id=int,
)

exercises.TermConnectionExercise.as_endpoint(
    router=exercise_router,
    path='/term-connection/{exercise_id}',
    ExerciseSchema=schema.TextConnectionView,
    choices=(list[int], Field(min_length=4, max_length=4)),
)
