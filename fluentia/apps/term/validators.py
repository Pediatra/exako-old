from ninja.errors import HttpError

from fluentia.apps.core.decorators import validate


@validate
def validate_term(): ...


@validate_term.register('TermLexical')
def validate_term_value_ref(instance):
    if not instance.term_value_ref:
        return

    if instance.term_value_ref == instance.term:
        raise HttpError(
            status_code=422,
            message='term_value_ref cannot be the same as term lexical reference.',
        )


@validate_term.register('TermPronunciation')
def validate_pronunciation_lexical_form(instance):
    if not instance.term_lexical:
        return

    if instance.term_lexical.term_value_ref:
        raise HttpError(
            status_code=422,
            message='lexical with term_value_ref cannot have a pronunciation.',
        )


@validate_term.register('TermExampleLink')
@validate_term.register('TermExampleTranslationLink')
def validate_lexical_example_link(instance):
    if not instance.term_lexical:
        return

    if instance.term_lexical.term_value_ref:
        raise HttpError(
            status_code=422,
            message='lexical with term_value_ref cannot have a example link.',
        )


@validate_term.register('TermDefinitionTranslation')
def validate_term_definition_translation_language_reference(instance):
    if instance.language == instance.term_definition.term.origin_language:
        raise HttpError(
            status_code=422,
            message='translation language reference cannot be same as language.',
        )


@validate_term.register('TermExampleTranslationLink')
def validate_term_example_translation_language_reference(instance):
    error = HttpError(
        status_code=422,
        message='translation language reference cannot be same as language.',
    )
    if instance.language == instance.term_example.language:
        raise error

    if instance.term and instance.language == instance.term.origin_language:
        raise error
    elif (
        instance.term_definition
        and instance.language == instance.term_definition.term.origin_language
    ):
        raise error
    elif (
        instance.term_lexical
        and instance.language == instance.term_lexical.term.origin_language
    ):
        raise error


@validate_term.register('TermExampleLink')
@validate_term.register('TermExampleTranslationLink')
def validate_term_example_language_reference(instance):
    error = HttpError(
        status_code=422,
        message='term example language has to be the same as the link models.',
    )

    if (
        instance.term
        and instance.term_example.language != instance.term.origin_language
    ):
        raise error
    elif (
        instance.term_definition
        and instance.term_example.language
        != instance.term_definition.term.origin_language
    ):
        raise error
    elif (
        instance.term_lexical
        and instance.term_example.language != instance.term_lexical.term.origin_language
    ):
        raise error
