from datetime import datetime

from ninja import Field, FilterSchema, Schema

from fluentia.apps.term.constants import Language


class CardSetSchema(Schema):
    name: str = Field(examples=['Palavras novas'])
    description: str | None = Field(
        default=None, examples=['Um cartão sobre palavras novas.']
    )
    language: Language | None = None


class CardSetList(FilterSchema):
    name: str | None = Field(
        default=None,
        description='Nome a ser filtrado.',
        q='name__ct_icontains',
    )


class CardSetSchemaView(CardSetSchema):
    id: int
    created_at: datetime
    modified_at: datetime | None = None


class CardSetSchemaUpdate(Schema):
    name: str | None = Field(examples=['Palavras novas'], default=None)
    description: str | None = Field(
        default=None, examples=['Um cartão sobre palavras novas.']
    )
    language: Language | None = None


class CardSchema(Schema):
    expression: str = Field(examples=['Casa'])
    origin_language: Language
    cardset_id: int
    note: str | None = Field(
        default=None,
        examples=['Casa pode ser um lugar grande.'],
        description='Pode usar HTML para escrevar as notas.',
    )


class CardList(FilterSchema):
    expression: str | None = Field(
        default=None,
        description='Filtrar por termo.',
        q='term__expression__ct_icontains',
    )
    note: str | None = Field(
        default=None,
        description='Filtrar por anotação.',
        q='note__ct_icontains',
    )


class CardSchemaView(Schema):
    id: int
    expression: str = Field(examples=['Casa'])
    origin_language: Language
    note: str | None = Field(
        default=None,
        examples=['Casa pode ser um lugar grande.'],
        description='Pode usar HTML para escrevar as notas.',
    )
    created_at: datetime
    modified_at: datetime | None = None

    @staticmethod
    def resolve_expression(obj):
        return obj.term.expression

    @staticmethod
    def resolve_origin_language(obj):
        return obj.term.origin_language


class CardSchemaUpdate(Schema):
    note: str | None = Field(default=None, examples=['Casa pode ser um lugar grande.'])
