from django.forms import model_to_dict
from django.urls import reverse_lazy
from ninja import Field, Schema
from pydantic import computed_field, field_validator, model_validator

from fluentia.apps.exercise.constants import ExerciseType
from fluentia.apps.term.constants import Language


class ExerciseSchemaBase(Schema):
    language: Language
    type: ExerciseType


class OrderSentenceSchema(ExerciseSchemaBase):
    term_example: int
    additional_content: dict | None = Field(
        default=None,
        examples=[{'distractors': [1, 3, 5, 7]}],
    )

    @field_validator('additional_content')
    @classmethod
    def validate_distractors(cls, additional_content: dict) -> dict:
        if 'distractors' in additional_content and not isinstance(
            additional_content['distractors'], list
        ):
            raise ValueError('invalid distractors format, it should be a id list.')
        return additional_content


class ListenTermSchema(ExerciseSchemaBase):
    term_pronunciation: int
    term: int
    term_lexical: int | None = None
    additional_content: dict | None = Field(
        default=None,
        examples=[{'example': 123}],
    )


class ListenSentenceSchema(ExerciseSchemaBase):
    term_pronunciation: int
    term_example: int
    additional_content: dict | None = Field(
        default=None,
        examples=[{'example': 123}],
    )


class ListenTermMChoiceSchema(ExerciseSchemaBase):
    term_pronunciation: int
    term: int
    additional_content: dict | None = Field(
        default=None,
        examples=[{'example': 123}],
    )


class SpeakTermSchema(ExerciseSchemaBase):
    term: int
    term_lexical: int | None = None
    additional_content: dict | None = Field(
        default=None,
        examples=[{'example': 123}],
    )


class SpeakSentenceSchema(ExerciseSchemaBase):
    term_example: int
    additional_content: dict | None = Field(
        default=None,
        examples=[{'example': 123}],
    )


class TermMChoiceSchema(ExerciseSchemaBase):
    term: int
    term_example: int
    term_lexical: int | None = None
    additional_content: dict = Field(
        examples=[{'distractors': [1, 3, 5, 7]}],
    )

    @field_validator('additional_content')
    @classmethod
    def validate_distractors(cls, additional_content: dict) -> dict:
        if 'distractors' not in additional_content or not isinstance(
            additional_content['distractors'], list
        ):
            raise ValueError(
                'invalid distractors format, exercise needs distractors to form the alternatives.'
            )
        return additional_content


class TermDefinitionMChoiceSchema(ExerciseSchemaBase):
    term_definition: int
    term: int
    additional_content: dict = Field(
        examples=[{'distractors': [1, 3, 5, 7]}],
    )

    @field_validator('additional_content')
    @classmethod
    def validate_distractors(cls, additional_content: dict) -> dict:
        if 'distractors' not in additional_content or not isinstance(
            additional_content['distractors'], list
        ):
            raise ValueError(
                'invalid distractors format, exercise needs distractors to form the alternatives.'
            )
        return additional_content


class TermImageMChoiceSchema(ExerciseSchemaBase):
    term: int
    term_image: int
    term_pronunciation: int
    additional_content: dict = Field(
        examples=[{'distractors': [1, 3, 5, 7]}],
    )

    @field_validator('additional_content')
    @classmethod
    def validate_distractors(cls, additional_content: dict) -> dict:
        if 'distractors' not in additional_content or not isinstance(
            additional_content['distractors'], list
        ):
            raise ValueError(
                'invalid distractors format, exercise needs distractors to form the alternatives.'
            )
        return additional_content


class TermImageTextMChoiceSchema(ExerciseSchemaBase):
    term: int
    term_image: int
    additional_content: dict = Field(
        examples=[{'distractors': [1, 3, 5, 7]}],
    )

    @field_validator('additional_content')
    @classmethod
    def validate_distractors(cls, additional_content: dict) -> dict:
        if 'distractors' not in additional_content or not isinstance(
            additional_content['distractors'], list
        ):
            raise ValueError(
                'invalid distractors format, exercise needs distractors to form the alternatives.'
            )
        return additional_content


class TermConnectionSchema(ExerciseSchemaBase):
    term: int
    additional_content: dict = Field(
        examples=[
            {
                'distractors': [1, 3, 5, 7, 8, 9, 11, 12],
                'connections': [1, 5, 7, 9],
            }
        ],
    )

    @field_validator('additional_content')
    @classmethod
    def validate_distractors(cls, additional_content: dict) -> dict:
        if 'distractors' not in additional_content or not isinstance(
            additional_content['distractors'], list
        ):
            raise ValueError(
                'invalid distractors format, exercise needs distractors to form the connections.'
            )
        if 'connections' not in additional_content or not isinstance(
            additional_content['connections'], list
        ):
            raise ValueError(
                'invalid connections format, exercise needs connections to form the connections.'
            )
        return additional_content


exercise_models: dict[ExerciseType, type[ExerciseSchemaBase]] = {
    ExerciseType.ORDER_SENTENCE: OrderSentenceSchema,
    ExerciseType.LISTEN_TERM: ListenTermSchema,
    ExerciseType.LISTEN_SENTENCE: ListenSentenceSchema,
    ExerciseType.LISTEN_TERM_MCHOICE: ListenTermMChoiceSchema,
    ExerciseType.SPEAK_TERM: SpeakTermSchema,
    ExerciseType.SPEAK_SENTENCE: SpeakSentenceSchema,
    ExerciseType.TERM_MCHOICE: TermMChoiceSchema,
    ExerciseType.TERM_DEFINITION_MCHOICE: TermDefinitionMChoiceSchema,
    ExerciseType.TERM_IMAGE_MCHOICE: TermImageMChoiceSchema,
    ExerciseType.TERM_IMAGE_TEXT_MCHOICE: TermImageTextMChoiceSchema,
    ExerciseType.TERM_CONNECTION: TermConnectionSchema,
}


class ExerciseSchema(ExerciseSchemaBase):
    term: int | None = None
    term_example: int | None = None
    term_pronunciation: int | None = None
    term_lexical: int | None = None
    term_definition: int | None = None
    term_image: int | None = None
    additional_content: dict | None = Field(default=None)

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
            ExerciseType.TERM_IMAGE_MCHOICE: 'api-1.0.0:term_image_mchoice_exercise',
            ExerciseType.TERM_IMAGE_TEXT_MCHOICE: 'api-1.0.0:term_image_text_mchoice_exercise',
            ExerciseType.TERM_CONNECTION: 'api-1.0.0:term_connection_exercise',
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


class ImageMChoiceView(ExerciseBaseView):
    audio_file: str
    choices: dict[int, str] = Field(
        examples=[
            [
                {
                    1: 'https://example.com',
                    2: 'https://example.com',
                    3: 'https://example.com',
                    4: 'https://example.com',
                }
            ]
        ],
        description='Será retornado sempre 4 alternativas contendo o id do termo referido e o link para imagem do termo.',
    )


class TextImageMChoiceView(ExerciseBaseView):
    image: str
    choices: list[str] = Field(examples=[['casa', 'avião', 'jaguar', 'parede']])


class TextConnectionView(ExerciseBaseView):
    choices: dict[int, str] = Field(
        examples=[
            [
                {
                    1: 'casa',
                    2: 'avião',
                    3: 'jaguar',
                    4: 'parede',
                }
            ]
        ],
    )


class TextConnectionCheck(Schema):
    choices: list[int] = Field(min_length=4, max_length=4)
