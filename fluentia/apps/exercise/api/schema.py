from django.forms import model_to_dict
from django.urls import reverse_lazy
from ninja import Field, Schema
from pydantic import computed_field, model_validator
from typing_extensions import ClassVar

from fluentia.apps.exercise.constants import ExerciseType
from fluentia.apps.term.constants import Language


class ExerciseSchemaBase(Schema):
    language: Language
    type: ExerciseType
    additional_content: dict | None = Field(
        default=None,
        examples=[{'distractors': [1, 3, 5, 7]}],
    )


class OrderSentenceSchema(ExerciseSchemaBase):
    term_example: int


class ListenTermSchema(ExerciseSchemaBase):
    term_pronunciation: int
    term: int
    term_lexical: int | None = None


class ListenSentenceSchema(ExerciseSchemaBase):
    term_pronunciation: int
    term_example: int


class ListenTermMChoiceSchema(ExerciseSchemaBase):
    term_pronunciation: int
    term: int


class SpeakTermSchema(ExerciseSchemaBase):
    term: int
    term_lexical: int | None = None


class SpeakSentenceSchema(ExerciseSchemaBase):
    term_example: int


class MChoiceTermSchema(ExerciseSchemaBase):
    term: int
    term_example: int
    term_lexical: int | None = None


class MChoiceTermDefinitionSchema(ExerciseSchemaBase):
    term_definition: int
    term: int


exercise_models: dict[ExerciseType, type[ExerciseSchemaBase]] = {
    ExerciseType.ORDER_SENTENCE: OrderSentenceSchema,
    ExerciseType.LISTEN_TERM: ListenTermSchema,
    ExerciseType.LISTEN_SENTENCE: ListenSentenceSchema,
    ExerciseType.LISTEN_TERM_MCHOICE: ListenTermMChoiceSchema,
    ExerciseType.SPEAK_TERM: SpeakTermSchema,
    ExerciseType.SPEAK_SENTENCE: SpeakSentenceSchema,
    ExerciseType.TERM_MCHOICE: MChoiceTermSchema,
    ExerciseType.TERM_DEFINITION_MCHOICE: MChoiceTermDefinitionSchema,
}


class ExerciseSchema(ExerciseSchemaBase):
    term: int | None = None
    term_example: int | None = None
    term_pronunciation: int | None = None
    term_lexical: int | None = None
    term_definition: int | None = None

    exercise_model: ClassVar[type[ExerciseSchemaBase]]

    @model_validator(mode='before')
    @classmethod
    def validation(cls, data):
        values = data._obj if isinstance(data._obj, dict) else model_to_dict(data._obj)
        exercise_type = values.get('type', None)
        Model = exercise_models.get(exercise_type)
        if Model is None:
            raise ValueError('invalid exercise type.')
        return Model(**values).model_dump()


class ExerciseSchemaView(ExerciseSchemaBase):
    id: int


class ExerciseView(Schema):
    id: int
    type: ExerciseType

    @computed_field(
        examples=['https://example.com/my-exercise/'],
        description='Usada para coletar a url que informará sobre o exercício requirido.',
    )
    @property
    def url(self) -> str:
        url_map = {
            ExerciseType.ORDER_SENTENCE: 'api-1.0.0:order_sentence_exercise',
            ExerciseType.LISTEN_TERM: 'api-1.0.0:listen_term_exercise',
            ExerciseType.LISTEN_TERM_MCHOICE: 'api-1.0.0:listen_term_mchoice_exercise',
            ExerciseType.LISTEN_SENTENCE: 'api-1.0.0:listen_sentence_exercise',
            ExerciseType.SPEAK_TERM: 'api-1.0.0:speak_term_exercise',
            ExerciseType.SPEAK_SENTENCE: 'api-1.0.0:speak_sentence_exercise',
            ExerciseType.TERM_MCHOICE: 'api-1.0.0:term_mchoice_exercise',
            ExerciseType.TERM_DEFINITION_MCHOICE: 'api-1.0.0:term_definition_mchoice_exercise',
        }

        url_name = url_map[self.type]
        return str(reverse_lazy(url_name, kwargs={'exercise_id': self.id}))


class ExerciseResponse(Schema):
    correct: bool
    correct_answer: str | None = None
    correct_percentage: float | None = None


class ExerciseBaseView(Schema):
    header: str = Field(examples=['Cabeçalho do exercício'])


class OrderSentenceView(ExerciseBaseView):
    sentence: list[str] = Field(
        examples=[['almoçei', 'na', 'Ontem', 'casa', 'da', 'eu', 'mãe', 'minha.']]
    )


class ListenView(ExerciseBaseView):
    audio_file: str = Field(examples=['https://example.com/my-audio.mp3'])


class TextCheck(Schema):
    text: str


class ListenMChoiceView(ExerciseBaseView):
    choices: dict[str, str] = Field(
        examples=[
            {
                'casa': 'https://example.com/my-audio.mp3',
                'asa': 'https://example.com/my-audio.mp3',
                'brasa': 'https://example.com/my-audio.mp3',
                'rasa': 'https://example.com/my-audio.mp3',
            }
        ],
        description='Será retornado sempre 4 alternativas, incluindo a correta.',
    )


class SpeakView(ExerciseBaseView):
    text_to_speak: str = Field(
        examples=['avião'],
        description='Texto a ser falado pelo usuário.',
    )


class MultipleChoiceView(ExerciseBaseView):
    choices: list[str] = Field(
        examples=[['casa', 'fogueira', 'semana', 'avião']],
        description='Será retornado sempre 4 alternativas, incluindo a correta.',
    )
