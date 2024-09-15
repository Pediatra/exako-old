from random import choice

import factory
from factory import fuzzy

from fluentia.apps.term.constants import Language, Level, PartOfSpeech, TermLexicalType
from fluentia.apps.term.models import (
    Term,
    TermDefinition,
    TermDefinitionTranslation,
    TermExample,
    TermExampleTranslation,
    TermImage,
    TermLexical,
    TermPronunciation,
)


class TermFactory(factory.django.DjangoModelFactory):
    expression = factory.Faker('sentence')
    origin_language = fuzzy.FuzzyChoice(Language)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = Term


class TermLexicalFactory(factory.django.DjangoModelFactory):
    value = factory.Faker('sentence')
    type = fuzzy.FuzzyChoice(TermLexicalType)
    term = factory.SubFactory(TermFactory)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = TermLexical


class TermExampleFactory(factory.django.DjangoModelFactory):
    language = Language.PORTUGUESE
    example = factory.Faker('sentence', nb_words=8)
    level = fuzzy.FuzzyChoice(Level)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = TermExample


class TermExampleTranslationFactory(factory.django.DjangoModelFactory):
    language = Language.CHINESE
    translation = factory.Faker('sentence')
    term_example = factory.SubFactory(TermExampleFactory)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = TermExampleTranslation


class TermDefinitionFactory(factory.django.DjangoModelFactory):
    level = fuzzy.FuzzyChoice(Level)
    part_of_speech = fuzzy.FuzzyChoice(PartOfSpeech)
    definition = factory.Faker('sentence')
    term = factory.SubFactory(TermFactory)
    term_lexical = factory.SubFactory(TermLexicalFactory)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = TermDefinition


class TermDefinitionTranslationFactory(factory.django.DjangoModelFactory):
    translation = factory.Faker('sentence')
    meaning = factory.Faker('sentence')
    term_definition = factory.SubFactory(TermDefinitionFactory)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        term_definition = kwargs['term_definition']
        if isinstance(term_definition, int):
            term_definition = TermDefinition.objects.get(id=term_definition)
        languages = [
            choice
            for choice, _ in Language.choices
            if choice != term_definition.term.origin_language
        ]
        kwargs['language'] = choice(languages)
        return kwargs

    class Meta:
        model = TermDefinitionTranslation


class TermPronunciationFactory(factory.django.DjangoModelFactory):
    audio_file = factory.Faker('url')
    description = factory.Faker('sentence')
    language = fuzzy.FuzzyChoice(Language)
    phonetic = factory.Faker('name')
    text = factory.Faker('sentence')
    term = factory.SubFactory(TermFactory)
    additional_content = {'syllable': ['ca', 'sa'], 'part': 'en'}

    class Meta:
        model = TermPronunciation


class TermImageFactory(factory.django.DjangoModelFactory):
    term = factory.SubFactory(TermFactory)
    image = factory.django.ImageField(color='blue')

    class Meta:
        model = TermImage
