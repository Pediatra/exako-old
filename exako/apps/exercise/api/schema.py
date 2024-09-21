from typing import Any

from django.forms import model_to_dict
from django.urls import reverse_lazy
from ninja import Field, Schema
from pydantic import computed_field, field_validator, model_validator

from exako.apps.exercise.constants import ExerciseSubType, ExerciseType
from exako.apps.term.constants import Language


def _validate_sub_exercise_type(self):
    if not any([self.term, self.term_lexical]) or all([self.term, self.term_lexical]):
        raise ValueError('provide term or term_lexical, but not both or neither.')

    if (
        not self.additional_content
        or 'sub_type' not in self.additional_content
        or self.additional_content['sub_type']
        not in [value for value, _ in ExerciseSubType.choices]
    ):
        raise ValueError('sub type is not defined.')


class ExerciseSchemaBase(Schema):
    language: Language
    type: ExerciseType


class OrderSentenceSchema(ExerciseSchemaBase):
    term_example: int
    additional_content: dict | None = Field(
        default=None,
        examples=[{'distractors': {'term': [1, 3, 5, 7]}}],
    )

    @field_validator('additional_content')
    @classmethod
    def validate_distractors(cls, additional_content: dict | None) -> dict | None:
        if (
            additional_content is not None
            and 'distractors' in additional_content
            and 'term' in additional_content['distractors']
            and not isinstance(additional_content['distractors']['term'], list)
        ):
            raise ValueError('invalid distractors format, it should be a id list.')
        return additional_content


class ListenTermSchema(ExerciseSchemaBase):
    term_pronunciation: int
    term: int | None = None
    term_lexical: int | None = None
    additional_content: dict | None = Field(
        examples=[{'sub_type': ExerciseSubType.TERM}]
    )

    validate_sub_exercise_type = model_validator(mode='after')(
        _validate_sub_exercise_type
    )


class ListenSentenceSchema(ExerciseSchemaBase):
    term_pronunciation: int
    term_example: int
    additional_content: dict | None = Field(default=None)


class ListenTermMChoiceSchema(ExerciseSchemaBase):
    term_pronunciation: int
    term: int
    additional_content: dict | None = Field(default=None)


class SpeakTermSchema(ExerciseSchemaBase):
    term: int | None = None
    term_lexical: int | None = None
    term_pronunciation: int
    additional_content: dict | None = Field(
        examples=[{'sub_type': ExerciseSubType.TERM}]
    )

    validate_sub_exercise_type = model_validator(mode='after')(
        _validate_sub_exercise_type
    )


class SpeakSentenceSchema(ExerciseSchemaBase):
    term_example: int
    term_pronunciation: int
    additional_content: dict | None = Field(default=None)


class TermMChoiceSchema(ExerciseSchemaBase):
    term: int | None = None
    term_lexical: int | None = None
    term_example: int
    additional_content: dict = Field(
        examples=[
            {
                'distractors': {
                    'term': [1, 3, 5, 7],
                    'term_lexical': [1, 5, 6, 8],
                },
                'sub_type': ExerciseSubType.TERM,
            }
        ],
    )

    @model_validator(mode='after')
    def validate_distractors(self):
        _validate_sub_exercise_type(self)
        sub_type = self.additional_content['sub_type']
        if sub_type == ExerciseSubType.TERM:
            if (
                'distractors' not in self.additional_content
                or 'term' not in self.additional_content['distractors']
            ):
                raise ValueError(
                    'invalid distractors format, exercise needs term distractors to form the alternatives.'
                )
        else:
            if (
                'distractors' not in self.additional_content
                or 'term_lexical' not in self.additional_content['distractors']
            ):
                raise ValueError(
                    'invalid distractors format, exercise needs term_lexical distractors to form the alternatives.'
                )

        if (
            sub_type == ExerciseSubType.TERM
            and not isinstance(self.additional_content['distractors']['term'], list)
            or sub_type
            in [
                ExerciseSubType.TERM_LEXICAL_TERM_REF,
                ExerciseSubType.TERM_LEXICAL_VALUE,
            ]
            and not isinstance(
                self.additional_content['distractors']['term_lexical'], list
            )
        ):
            raise ValueError('invalid distractors format, it should be a id list.')
        return self


class TermDefinitionMChoiceSchema(ExerciseSchemaBase):
    term_definition: int
    term: int
    additional_content: dict = Field(
        examples=[{'distractors': {'term_definition': [1, 3, 5, 7]}}],
    )

    @field_validator('additional_content')
    @classmethod
    def validate_distractors(cls, additional_content: dict) -> dict:
        if (
            'distractors' not in additional_content
            or 'term_definition' not in additional_content['distractors']
        ):
            raise ValueError(
                'invalid distractors format, exercise needs distractors to form the alternatives.'
            )
        if not isinstance(additional_content['distractors']['term_definition'], list):
            raise ValueError('invalid distractors format, it should be a id list.')
        return additional_content


class TermImageMChoiceSchema(ExerciseSchemaBase):
    term: int
    term_image: int
    term_pronunciation: int
    additional_content: dict = Field(
        examples=[{'distractors': {'term_image': [1, 3, 5, 7]}}],
    )

    @field_validator('additional_content')
    @classmethod
    def validate_distractors(cls, additional_content: dict) -> dict:
        if (
            'distractors' not in additional_content
            or 'term_image' not in additional_content['distractors']
        ):
            raise ValueError(
                'invalid distractors format, exercise needs distractors to form the alternatives.'
            )
        if not isinstance(additional_content['distractors']['term_image'], list):
            raise ValueError('invalid distractors format, it should be a id list.')
        return additional_content


class TermImageMChoiceTextSchema(ExerciseSchemaBase):
    term: int
    term_image: int
    additional_content: dict = Field(
        examples=[{'distractors': {'term': [1, 3, 5, 7]}}],
    )

    @field_validator('additional_content')
    @classmethod
    def validate_distractors(cls, additional_content: dict) -> dict:
        if (
            'distractors' not in additional_content
            or 'term' not in additional_content['distractors']
        ):
            raise ValueError(
                'invalid distractors format, exercise needs distractors to form the alternatives.'
            )
        if not isinstance(additional_content['distractors']['term'], list):
            raise ValueError('invalid distractors format, it should be a id list.')
        return additional_content


class TermConnectionSchema(ExerciseSchemaBase):
    term: int
    additional_content: dict = Field(
        examples=[
            {
                'distractors': {'term': [1, 3, 5, 7, 8, 9, 11, 12]},
                'connections': {'term': [1, 5, 7, 9]},
            }
        ],
    )

    @field_validator('additional_content')
    @classmethod
    def validate_distractors(cls, additional_content: dict) -> dict:
        if (
            'distractors' not in additional_content
            or 'term' not in additional_content['distractors']
        ):
            raise ValueError(
                'invalid distractors format, exercise needs distractors to form the connections.'
            )
        if not isinstance(additional_content['distractors']['term'], list):
            raise ValueError('invalid distractors format, it should be a id list.')

        if (
            'connections' not in additional_content
            or 'term' not in additional_content['connections']
        ):
            raise ValueError(
                'invalid connections format, exercise needs connections to form the connections.'
            )
        if not isinstance(additional_content['connections']['term'], list):
            raise ValueError('invalid connections format, it should be a id list.')
        return additional_content


exercise_map: dict[ExerciseType, type[ExerciseSchemaBase]] = {
    ExerciseType.ORDER_SENTENCE: OrderSentenceSchema,
    ExerciseType.LISTEN_TERM: ListenTermSchema,
    ExerciseType.LISTEN_SENTENCE: ListenSentenceSchema,
    ExerciseType.LISTEN_TERM_MCHOICE: ListenTermMChoiceSchema,
    ExerciseType.SPEAK_TERM: SpeakTermSchema,
    ExerciseType.SPEAK_SENTENCE: SpeakSentenceSchema,
    ExerciseType.TERM_MCHOICE: TermMChoiceSchema,
    ExerciseType.TERM_DEFINITION_MCHOICE: TermDefinitionMChoiceSchema,
    ExerciseType.TERM_IMAGE_MCHOICE: TermImageMChoiceSchema,
    ExerciseType.TERM_IMAGE_MCHOICE_TEXT: TermImageMChoiceTextSchema,
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
        Model = exercise_map.get(exercise_type)
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
            ExerciseType.TERM_IMAGE_MCHOICE_TEXT: 'api-1.0.0:term_image_mchoice_text_exercise',
            ExerciseType.TERM_CONNECTION: 'api-1.0.0:term_connection_exercise',
        }

        url_name = url_map[self.type]
        return str(reverse_lazy(url_name, kwargs={'exercise_id': self.id}))


class ExerciseResponse(Schema):
    correct: bool
    correct_answer: Any | None = None


class ExerciseBaseView(Schema):
    header: str = Field(examples=['Cabeçalho do exercício'])
    title: str = Field(examples=['Título do exercício'])
    description: str = Field(
        examples=['Descrição e instruções de como jogar o exercício.']
    )


class OrderSentenceView(ExerciseBaseView):
    sentence: list[str] = Field(
        examples=[['almoçei', 'na', 'Ontem', 'casa', 'da', 'eu', 'mãe', 'minha.']]
    )


class ListenView(ExerciseBaseView):
    audio_file: str = Field(examples=['https://example.com/my-audio.mp3'])


class ListenMChoiceView(ExerciseBaseView):
    choices: dict[int, dict] = Field(
        examples=[
            {
                1: {
                    'expression': 'casa',
                    'audio_file': 'https://example.com/my-audio.mp3',
                },
                2: {
                    'expression': 'asa',
                    'audio_file': 'https://example.com/my-audio.mp3',
                },
                3: {
                    'expression': 'brasa',
                    'audio_file': 'https://example.com/my-audio.mp3',
                },
                4: {
                    'expression': 'rasa',
                    'audio_file': 'https://example.com/my-audio.mp3',
                },
            }
        ],
        description='Será retornado sempre 4 alternativas, incluindo a correta.',
    )


class SpeakView(ExerciseBaseView):
    audio_file: str | None = Field(
        examples=['https://example.com/my-audio.mp3'],
        default=None,
    )
    phonetic: str = Field(examples=['/ˈhaʊ.zɪz/'])


class TermMChoiceView(ExerciseBaseView):
    choices: dict[int, str] = Field(
        examples=[{1: 'casa', 2: 'fogueira', 3: 'semana', 4: 'avião'}],
        description='Será retornado sempre 4 alternativas, incluindo a correta.',
    )


class ImageMChoiceView(ExerciseBaseView):
    audio_file: str = Field(examples=['https://example.com/my-audio.mp3'])
    choices: dict[int, str] = Field(
        examples=[
            {
                1: 'https://example.com',
                2: 'https://example.com',
                3: 'https://example.com',
                4: 'https://example.com',
            }
        ],
        description='Será retornado sempre 4 alternativas contendo o id do termo referido e o link para imagem do termo.',
    )


class TextImageMChoiceView(ExerciseBaseView):
    image: str = Field(examples=['https://example.com/my-image.png'])
    choices: dict[int, str] = Field(
        examples=[
            {
                1: 'casa',
                2: 'avião',
                3: 'jaguar',
                4: 'parede',
            }
        ],
        description='Será retornado sempre 4 alternativas contendo o id do termo referido e o link para imagem do termo.',
    )


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
