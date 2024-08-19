from ninja import Field, FilterSchema, Schema
from pydantic import model_validator

from fluentia.apps.term import constants


class TermSchema(Schema):
    expression: str = Field(examples=['Casa'])
    origin_language: constants.Language
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermView(Schema):
    id: int
    expression: str = Field(examples=['Casa'])
    origin_language: constants.Language
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermPronunciationLinkSchema(FilterSchema):
    term: int | None = None
    term_example: int | None = None
    term_lexical: int | None = None

    @model_validator(mode='after')
    def link_validator(self):
        link_attributes = {
            field: getattr(self, field)
            for field in {
                'term',
                'term_example',
                'term_lexical',
            }
            if getattr(self, field, None) is not None
        }
        link_count = len(link_attributes.values())
        if link_count == 0:
            raise ValueError('you need to provide at least one object to link.')
        if link_count > 1:
            raise ValueError('you can reference only one object.')
        return self


class TermPronunciationSchema(TermPronunciationLinkSchema):
    phonetic: str = Field(examples=['/ˈhaʊ.zɪz/'])
    language: constants.Language
    text: str = Field(examples=['Texto que está sendo pronunciado.'])
    audio_file: str | None = Field(
        default=None, examples=['https://mylink.com/my-audio.mp3']
    )
    description: str | None = Field(examples=['português do brasil'], default=None)
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermPronunciationView(Schema):
    id: int
    phonetic: str = Field(examples=['/ˈhaʊ.zɪz/'])
    language: constants.Language
    text: str = Field(examples=['Texto que está sendo pronunciado.'])
    audio_file: str | None = Field(
        default=None, examples=['https://mylink.com/my-audio.mp3']
    )
    description: str | None = Field(examples=['português do brasil'], default=None)
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermDefinitionSchema(Schema):
    part_of_speech: constants.PartOfSpeech = Field(examples=(['noun']))
    definition: str = Field(
        examples=['Set of walls, rooms, and roof with specific purpose of habitation.']
    )
    term: int
    level: constants.Level | None = None
    term_lexical: int | None = None
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermDefinitionView(Schema):
    id: int
    part_of_speech: constants.PartOfSpeech = Field(examples=(['noun']))
    definition: str = Field(
        examples=['Set of walls, rooms, and roof with specific purpose of habitation.']
    )
    level: constants.Level | None = None
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class ListTermDefintionFilter(FilterSchema):
    term: int
    part_of_speech: constants.PartOfSpeech | None = None
    level: constants.Level | None = None
    term_lexical: int | None = None


class TermDefinitionTranslationSchema(Schema):
    term_definition: int
    language: constants.Language
    meaning: str = Field(examples=['Casa, lar'])
    translation: str = Field(
        examples=['Conjunto de parades, quartos e teto com a finalidade de habitação.'],
    )
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermDefinitionTranslationView(Schema):
    language: constants.Language
    meaning: str = Field(examples=['Casa, lar'])
    translation: str = Field(
        examples=['Conjunto de parades, quartos e teto com a finalidade de habitação.'],
    )
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class ExampleHighlightValidator:
    @model_validator(mode='after')
    def validate_highlight(self):
        example = getattr(self, 'example', None) or getattr(self, 'translation')

        intervals = []
        for value in self.highlight:
            if len(value) != 2:
                raise ValueError(
                    'highlight must consist of pairs of numbers representing the start and end positions.'
                )

            v1, v2 = value
            example_len = len(example) - 1
            if v1 > example_len or v2 > example_len:
                raise ValueError(
                    'highlight cannot be greater than the length of the example.'
                )
            if v1 < 0 or v2 < 0:
                raise ValueError(
                    'both highlight values must be greater than or equal to 0.'
                )
            if v1 > v2:
                raise ValueError(
                    'highlight beginning value cannot be greater than the ending value, since it represents the start and end positions.'
                )

            interval = range(v1, v2 + 1)
            if any([i in intervals for i in interval]):
                raise ValueError(
                    'highlight interval must not overlap with any other intervals in highlight list.'
                )
            intervals.extend(interval)

        return self


class TermExampleLinkSchema(FilterSchema):
    term: int | None = None
    term_definition: int | None = None
    term_lexical: int | None = None

    @model_validator(mode='after')
    def link_validator(self):
        link_attributes = {
            field: getattr(self, field)
            for field in {
                'term',
                'term_definition',
                'term_lexical',
            }
            if getattr(self, field, None) is not None
        }
        link_count = len(link_attributes.values())
        if link_count == 0:
            raise ValueError('you need to provide at least one object to link.')
        if link_count > 1:
            raise ValueError('you can reference only one object.')
        return self


class TermExampleSchema(TermExampleLinkSchema, ExampleHighlightValidator):
    language: constants.Language
    example: str = Field(examples=["Yesterday a have lunch in my mother's house."])
    highlight: list[list[int]] = Field(
        examples=[[[4, 8], [11, 16]]],
        description='Highlighted positions in the given sentence where the term appears.',
    )
    level: constants.Level | None = None
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermExampleView(Schema):
    id: int
    language: constants.Language
    example: str = Field(examples=["Yesterday a have lunch in my mother's house."])
    highlight: list[list[int]] = Field(
        examples=[[[4, 8], [11, 16]]],
        description='Highlighted positions in the given sentence where the term appears.',
    )
    level: constants.Level | None = None
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermExampleTranslationView(Schema):
    language: constants.Language
    translation: str = Field(
        examples=['Ontem eu almoçei na casa da minha mãe.'],
    )
    highlight: list[list[int]] = Field(
        examples=[[[4, 8], [11, 16]]],
        description='Highlighted positions in the given translation sentence where the term appears.',
    )
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermExampleTranslationSchema(
    TermExampleLinkSchema,
    ExampleHighlightValidator,
):
    term_example: int
    language: constants.Language
    translation: str = Field(
        examples=['Ontem eu almoçei na casa da minha mãe.'],
    )
    highlight: list[list[int]] = Field(
        examples=[[[4, 8], [11, 16]]],
        description='Highlighted positions in the given translation sentence where the term appears.',
    )
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )


class TermLexicalSchema(Schema):
    term: int
    value: str | None = Field(examples=['Lar'], default=None)
    term_value_ref: int | None = None
    type: constants.TermLexicalType
    additional_content: dict | None = Field(
        default=None,
        examples=[{'syllable': ['ca', 'sa'], 'part': 'en'}],
    )

    @model_validator(mode='after')
    def validation(self):
        if not any([self.value, self.term_value_ref]):
            raise ValueError('you need to provied at least one value ref.')
        if all([self.value, self.term_value_ref]):
            raise ValueError(
                'you cannot reference two values at once (value, term_value_ref).'
            )
        return self


class TermLexicalView(Schema):
    id: int
    value: str | None = Field(examples=['Lar'], default=None)
    term_value_ref: TermView | None = None
    type: constants.TermLexicalType


class TermLexicalFilter(FilterSchema):
    term: int
    type: constants.TermLexicalType | None = None
