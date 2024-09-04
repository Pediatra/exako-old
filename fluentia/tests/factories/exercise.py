import factory

from fluentia.apps.exercise.constants import ExerciseType
from fluentia.apps.exercise.models import Exercise
from fluentia.apps.term.constants import Language, TermLexicalType
from fluentia.apps.term.models import TermExampleLink
from fluentia.tests.factories.term import (
    TermDefinitionFactory,
    TermExampleFactory,
    TermFactory,
    TermImageFactory,
    TermLexicalFactory,
    TermPronunciationFactory,
)


class _ExerciseBase(factory.django.DjangoModelFactory):
    language = factory.fuzzy.FuzzyChoice(Language)

    @classmethod
    def build(cls, *args, **kwargs):
        build = super().build(*args, **kwargs)
        foreign_keys = [
            'term',
            'term_example',
            'term_pronunciation',
            'term_lexical',
            'term_definition',
            'term_image',
        ]
        for fk in foreign_keys:
            obj = getattr(build, fk, None)
            if obj is None:
                continue
            obj.save()
        return build

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
        additional_content = {'distractors': cls._make_distractors()}
        kwargs.update(additional_content=additional_content)
        return super()._build(*args, **kwargs)

    @classmethod
    def _create(cls, *args, **kwargs):
        additional_content = {'distractors': cls._make_distractors()}
        kwargs.update(additional_content=additional_content)
        return super()._create(*args, **kwargs)


class ListenTermFactory(_ExerciseBase):
    type = ExerciseType.LISTEN_TERM
    term = factory.SubFactory(TermFactory)
    term_pronunciation = factory.SubFactory(
        TermPronunciationFactory,
        term=factory.SelfAttribute('..term'),
    )


class ListenTermLexicalFactory(ListenTermFactory):
    term_lexical = factory.SubFactory(
        TermLexicalFactory,
        term=factory.SelfAttribute('..term'),
    )


class ListenSentenceFactory(_ExerciseBase):
    type = ExerciseType.LISTEN_SENTENCE
    term_example = factory.SubFactory(TermExampleFactory)
    term_pronunciation = factory.SubFactory(
        TermPronunciationFactory,
        term=None,
        term_example=factory.SelfAttribute('..term_example'),
    )


class ListenTermMChoiceFactory(_ExerciseBase):
    type = ExerciseType.LISTEN_TERM_MCHOICE
    term = factory.SubFactory(TermFactory)
    term_pronunciation = factory.SubFactory(
        TermPronunciationFactory,
        term=factory.SelfAttribute('..term'),
    )

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
    def build(cls, *args, **kwargs):
        exercise = super().build(*args, **kwargs)
        cls._make_alternatives(exercise.term)
        return exercise

    @classmethod
    def _create(cls, *args, **kwargs):
        cls._make_alternatives(kwargs.get('term'))
        return super()._create(*args, **kwargs)


class SpeakTermFactory(_ExerciseBase):
    type = ExerciseType.SPEAK_TERM
    term = factory.SubFactory(TermFactory)


class SpeakTermLexicalFactory(SpeakTermFactory):
    term_lexical = factory.SubFactory(
        TermLexicalFactory,
        term=factory.SelfAttribute('..term'),
    )


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
        kwargs.update(additional_content={'distractors': cls._make_distractors()})
        return super()._build(*args, **kwargs)

    @classmethod
    def _create(cls, *args, **kwargs):
        TermExampleLink.objects.get_or_create(
            highlight=[[1, 5], [7, 9]],
            term_example=kwargs.get('term_example'),
            term=kwargs.get('term'),
            term_lexical=kwargs.get('term_lexical'),
        )
        kwargs.update(additional_content={'distractors': cls._make_distractors()})
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
    term_lexical = factory.SubFactory(
        TermLexicalFactory,
        term=factory.SelfAttribute('..term'),
    )


class TermDefinitionMChoiceFactory(_ExerciseBase):
    type = ExerciseType.TERM_DEFINITION_MCHOICE
    term = factory.SubFactory(TermFactory)
    term_definition = factory.SubFactory(
        TermDefinitionFactory,
        term_lexical=None,
        term=factory.SelfAttribute('..term'),
    )

    @staticmethod
    def _make_distractors():
        distractors = TermDefinitionFactory.create_batch(size=3)
        return [distractor.id for distractor in distractors]

    @classmethod
    def build(cls, *args, **kwargs):
        kwargs.update(additional_content={'distractors': cls._make_distractors()})
        return super().build(*args, **kwargs)

    @classmethod
    def create(cls, *args, **kwargs):
        kwargs.update(additional_content={'distractors': cls._make_distractors()})
        return super().create(*args, **kwargs)


class TermImageMChoiceFactory(_ExerciseBase):
    type = ExerciseType.TERM_IMAGE_MCHOICE
    term = factory.SubFactory(TermFactory)
    term_image = factory.SubFactory(
        TermImageFactory,
        term=factory.SelfAttribute('..term'),
    )
    term_pronunciation = factory.SubFactory(
        TermPronunciationFactory,
        term=factory.SelfAttribute('..term'),
    )

    @staticmethod
    def _make_distractors():
        distractors = TermFactory.create_batch(size=3)
        [TermImageFactory(term=distractor) for distractor in distractors]
        return [distractor.id for distractor in distractors]

    @classmethod
    def build(cls, *args, **kwargs):
        kwargs.update(additional_content={'distractors': cls._make_distractors()})
        return super().build(*args, **kwargs)

    @classmethod
    def create(cls, *args, **kwargs):
        kwargs.update(additional_content={'distractors': cls._make_distractors()})
        return super().create(*args, **kwargs)


class TermImageMChoiceTextFactory(_ExerciseBase):
    type = ExerciseType.TERM_IMAGE_TEXT_MCHOICE
    term = factory.SubFactory(TermFactory)
    term_image = factory.SubFactory(
        TermImageFactory,
        term=factory.SelfAttribute('..term'),
    )

    @staticmethod
    def _make_distractors():
        distractors = TermFactory.create_batch(size=3)
        return [distractor.id for distractor in distractors]

    @classmethod
    def build(cls, *args, **kwargs):
        kwargs.update(additional_content={'distractors': cls._make_distractors()})
        return super().build(*args, **kwargs)

    @classmethod
    def create(cls, *args, **kwargs):
        kwargs.update(additional_content={'distractors': cls._make_distractors()})
        return super().create(*args, **kwargs)


class TermConnectionFactory(_ExerciseBase):
    type = ExerciseType.TERM_CONNECTION
    term = factory.SubFactory(TermFactory)

    @staticmethod
    def _make_distractors():
        distractors = TermFactory.create_batch(size=8)
        return [distractor.id for distractor in distractors]

    @staticmethod
    def _make_connections():
        connections = TermFactory.create_batch(size=8)
        return [connection.id for connection in connections]

    @classmethod
    def build(cls, *args, **kwargs):
        kwargs.update(
            additional_content={
                'distractors': cls._make_distractors(),
                'connections': cls._make_connections(),
            }
        )
        return super().build(*args, **kwargs)

    @classmethod
    def create(cls, *args, **kwargs):
        kwargs.update(
            additional_content={
                'distractors': cls._make_distractors(),
                'connections': cls._make_connections(),
            }
        )
        return super().create(*args, **kwargs)
