import factory

from fluentia.apps.exercise.constants import ExerciseType
from fluentia.apps.exercise.models import Exercise
from fluentia.apps.term.constants import Language, TermLexicalType
from fluentia.apps.term.models import (
    Term,
    TermDefinition,
    TermExample,
    TermExampleLink,
    TermLexical,
    TermPronunciation,
)
from fluentia.tests.factories.term import (
    TermDefinitionFactory,
    TermExampleFactory,
    TermFactory,
    TermLexicalFactory,
    TermPronunciationFactory,
)


class _ExerciseBase(factory.django.DjangoModelFactory):
    language = factory.fuzzy.FuzzyChoice(Language)

    @classmethod
    def _build(cls, *args, **kwargs):
        factories = {
            Term: TermFactory,
            TermExample: TermExampleFactory,
            TermPronunciation: TermPronunciationFactory,
            TermLexical: TermLexicalFactory,
            TermDefinition: TermDefinitionFactory,
        }
        to_update = {}
        for key, value in kwargs.items():
            factory = factories.get(value.__class__)
            if factory:
                if value.id is not None:
                    continue
                to_update[key] = factory()
        kwargs.update(to_update)
        return super()._build(*args, **kwargs)

    @classmethod
    def _create(cls, *args, **kwargs):
        factories = {
            Term: TermFactory,
            TermExample: TermExampleFactory,
            TermPronunciation: TermPronunciationFactory,
            TermLexical: TermLexicalFactory,
            TermDefinition: TermDefinitionFactory,
        }
        to_update = {}
        for key, value in kwargs.items():
            factory = factories.get(value.__class__)
            if factory:
                if value.id is not None:
                    continue
                to_update[key] = factory()
        kwargs.update(to_update)
        return super()._create(*args, **kwargs)

    class Meta:
        model = Exercise


class OrderSentenceFactory(_ExerciseBase):
    type = ExerciseType.ORDER_SENTENCE
    term_example = factory.SubFactory(TermExampleFactory)

    @staticmethod
    def _make_distractors():
        distractors = TermFactory.create_batch(size=3)
        return [distractor.id for distractor in distractors]

    @classmethod
    def _build(cls, *args, **kwargs):
        additional_content = {'distractors': OrderSentenceFactory._make_distractors()}
        kwargs.update(additional_content=additional_content)
        return super()._build(*args, **kwargs)

    @classmethod
    def _create(cls, *args, **kwargs):
        additional_content = {'distractors': OrderSentenceFactory._make_distractors()}
        kwargs.update(additional_content=additional_content)
        return super()._create(*args, **kwargs)


class ListenTermFactory(_ExerciseBase):
    type = ExerciseType.LISTEN_TERM
    term = factory.SubFactory(TermFactory)
    term_pronunciation = factory.SubFactory(TermPronunciationFactory)


class ListenTermLexicalFactory(ListenTermFactory):
    term_lexical = factory.SubFactory(TermLexicalFactory)


class ListenSentenceFactory(_ExerciseBase):
    type = ExerciseType.LISTEN_SENTENCE
    term_example = factory.SubFactory(TermExampleFactory)
    term_pronunciation = factory.SubFactory(TermPronunciationFactory)


class ListenTermMChoiceFactory(_ExerciseBase):
    type = ExerciseType.LISTEN_TERM_MCHOICE
    term = factory.SubFactory(TermFactory)
    term_pronunciation = factory.SubFactory(TermPronunciationFactory)

    @staticmethod
    def _make_alternatives(term):
        lexicals = [
            TermLexicalFactory(
                **{'term_id': term} if isinstance(term, int) else {'term': term},
                type=TermLexicalType.RHYME,
                term_value_ref=TermFactory(),
            )
            for _ in range(3)
        ]
        [TermPronunciationFactory(term=lexical.term_value_ref) for lexical in lexicals]

    @classmethod
    def _build(cls, *args, **kwargs):
        exercise = super()._build(*args, **kwargs)
        ListenTermMChoiceFactory._make_alternatives(exercise.term)
        return exercise

    @classmethod
    def _create(cls, *args, **kwargs):
        ListenTermMChoiceFactory._make_alternatives(kwargs.get('term'))
        return super()._create(*args, **kwargs)


class SpeakTermFactory(_ExerciseBase):
    type = ExerciseType.SPEAK_TERM
    term = factory.SubFactory(TermFactory)


class SpeakTermLexicalFactory(SpeakTermFactory):
    term_lexical = factory.SubFactory(TermLexicalFactory)


class SpeakSentenceFactory(_ExerciseBase):
    type = ExerciseType.SPEAK_SENTENCE
    term_example = factory.SubFactory(TermExampleFactory)


class TermMChoiceFactory(_ExerciseBase):
    type = ExerciseType.TERM_MCHOICE
    term = factory.SubFactory(TermFactory)
    term_example = factory.SubFactory(TermExampleFactory)

    @staticmethod
    def _make_distractors():
        distractors = TermFactory.create_batch(size=3)
        return [distractor.id for distractor in distractors]

    @classmethod
    def _build(cls, *args, **kwargs):
        kwargs.update(
            additional_content={'distractors': TermMChoiceFactory._make_distractors()}
        )
        return super()._build(*args, **kwargs)

    @classmethod
    def _create(cls, *args, **kwargs):
        TermExampleLink.objects.get_or_create(
            highlight=[[1, 5], [7, 9]],
            term_example=kwargs.get('term_example'),
            term=kwargs.get('term'),
            term_lexical=kwargs.get('term_lexical'),
        )
        kwargs.update(
            additional_content={'distractors': TermMChoiceFactory._make_distractors()}
        )
        return super()._create(*args, **kwargs)

    @classmethod
    def build(cls, *args, **kwargs):
        build = super().build(*args, **kwargs)
        TermExampleLink.objects.get_or_create(
            highlight=[[1, 5], [7, 9]],
            term_example=build.term_example,
            term=build.term,
            term_lexical=build.term_lexical,
        )
        return build


class TermLexicalMChoiceFactory(TermMChoiceFactory):
    term_lexical = factory.SubFactory(TermLexicalFactory)


class TermDefinitionMChoiceFactory(_ExerciseBase):
    type = ExerciseType.TERM_DEFINITION_MCHOICE
    term = factory.SubFactory(TermFactory)
    term_definition = factory.SubFactory(TermDefinitionFactory)

    @staticmethod
    def _make_distractors():
        distractors = TermDefinitionFactory.create_batch(size=3)
        return [distractor.id for distractor in distractors]

    @classmethod
    def _build(cls, *args, **kwargs):
        kwargs.update(
            additional_content={
                'distractors': TermDefinitionMChoiceFactory._make_distractors()
            }
        )
        return super()._build(*args, **kwargs)

    @classmethod
    def _create(cls, *args, **kwargs):
        kwargs.update(
            additional_content={
                'distractors': TermDefinitionMChoiceFactory._make_distractors()
            }
        )
        return super()._create(*args, **kwargs)
