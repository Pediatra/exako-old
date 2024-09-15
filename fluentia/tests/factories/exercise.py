import factory

from fluentia.apps.exercise.constants import ExerciseSubType, ExerciseType
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
    def _save_object(cls, instance):
        foreign_keys = [
            'term',
            'term_lexical',
            'term_example',
            'term_pronunciation',
            'term_definition',
            'term_image',
        ]
        for fk in foreign_keys:
            obj = getattr(instance, fk, None)
            if obj is None:
                continue
            cls._save_object(obj)
            obj.save()

    @classmethod
    def build(cls, *args, **kwargs):
        build = super().build(*args, **kwargs)
        cls._save_object(build)
        return build

    class Meta:
        model = Exercise


class OrderSentenceFactory(_ExerciseBase):
    type = ExerciseType.ORDER_SENTENCE
    term_example = factory.SubFactory(TermExampleFactory)

    @staticmethod
    def _make_distractors():
        distractors = TermFactory.create_batch(size=6)
        return {'term': [distractor.id for distractor in distractors]}

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
    additional_content = {'sub_type': ExerciseSubType.TERM}


class ListenTermLexicalFactory(_ExerciseBase):
    type = ExerciseType.LISTEN_TERM
    term_lexical = factory.SubFactory(TermLexicalFactory)
    term_pronunciation = factory.SubFactory(
        TermPronunciationFactory,
        term=None,
        term_lexical=factory.SelfAttribute('..term_lexical'),
    )
    additional_content = {'sub_type': ExerciseSubType.TERM_LEXICAL_VALUE}


class ListenTermLexicalTermRefFactory(_ExerciseBase):
    type = ExerciseType.LISTEN_TERM
    additional_content = {'sub_type': ExerciseSubType.TERM_LEXICAL_TERM_REF}

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        term_value_ref = TermFactory()
        term_lexical = TermLexicalFactory(value=None, term_value_ref=term_value_ref)
        term_pronunciation = TermPronunciationFactory(term=term_value_ref)
        kwargs['term_lexical'] = term_lexical
        kwargs['term_pronunciation'] = term_pronunciation
        return kwargs


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
            for _ in range(6)
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
    term_pronunciation = factory.SubFactory(
        TermPronunciationFactory,
        term=factory.SelfAttribute('..term'),
    )
    additional_content = {'sub_type': ExerciseSubType.TERM}


class SpeakTermLexicalFactory(_ExerciseBase):
    type = ExerciseType.SPEAK_TERM
    term_lexical = factory.SubFactory(TermLexicalFactory)
    term_pronunciation = factory.SubFactory(
        TermPronunciationFactory,
        term=None,
        term_lexical=factory.SelfAttribute('..term_lexical'),
    )
    additional_content = {'sub_type': ExerciseSubType.TERM_LEXICAL_VALUE}


class SpeakTermLexicalTermRefFactory(_ExerciseBase):
    type = ExerciseType.SPEAK_TERM
    additional_content = {'sub_type': ExerciseSubType.TERM_LEXICAL_TERM_REF}

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        term_value_ref = TermFactory()
        term_lexical = TermLexicalFactory(value=None, term_value_ref=term_value_ref)
        term_pronunciation = TermPronunciationFactory(term=term_value_ref)
        kwargs['term_lexical'] = term_lexical
        kwargs['term_pronunciation'] = term_pronunciation
        return kwargs


class SpeakSentenceFactory(_ExerciseBase):
    type = ExerciseType.SPEAK_SENTENCE
    term_example = factory.SubFactory(TermExampleFactory)
    term_pronunciation = factory.SubFactory(
        TermPronunciationFactory,
        term=None,
        term_example=factory.SelfAttribute('..term_example'),
    )


class TermMChoiceFactory(_ExerciseBase):
    type = ExerciseType.TERM_MCHOICE
    term = factory.SubFactory(TermFactory)
    term_example = factory.SubFactory(TermExampleFactory)

    @staticmethod
    def _make_distractors():
        distractors = TermFactory.create_batch(size=6)
        return {'term': [distractor.id for distractor in distractors]}

    @classmethod
    def _make_additional_content(cls):
        return {
            'additional_content': {
                'distractors': cls._make_distractors(),
                'sub_type': ExerciseSubType.TERM,
            }
        }

    @classmethod
    def _build(cls, *args, **kwargs):
        kwargs.update(cls._make_additional_content())
        return super()._build(*args, **kwargs)

    @classmethod
    def _create(cls, *args, **kwargs):
        TermExampleLink.objects.get_or_create(
            highlight=[[1, 5], [7, 9]],
            term_example=kwargs.get('term_example'),
            term=kwargs.get('term'),
            term_lexical=kwargs.get('term_lexical'),
        )
        kwargs.update(cls._make_additional_content())
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
    term = None
    term_lexical = factory.SubFactory(TermLexicalFactory)

    @staticmethod
    def _make_distractors():
        distractors = TermLexicalFactory.create_batch(size=6)
        return {'term_lexical': [distractor.id for distractor in distractors]}

    @classmethod
    def _make_additional_content(cls):
        return {
            'additional_content': {
                'distractors': cls._make_distractors(),
                'sub_type': ExerciseSubType.TERM_LEXICAL_VALUE,
            }
        }


class TermLexicalTermRefMChoiceFactory(TermMChoiceFactory):
    term = None

    @classmethod
    def _make_additional_content(cls):
        return {
            'additional_content': {
                'distractors': cls._make_distractors(),
                'sub_type': ExerciseSubType.TERM_LEXICAL_TERM_REF,
            }
        }

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        term_value_ref = TermFactory()
        term_lexical = TermLexicalFactory(value=None, term_value_ref=term_value_ref)
        kwargs['term_lexical'] = term_lexical
        return kwargs


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
        distractors = TermDefinitionFactory.create_batch(size=6)
        return {'term_definition': [distractor.id for distractor in distractors]}

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
        return {
            'term_image': [
                TermImageFactory(term=distractor).id
                for distractor in TermFactory.create_batch(size=6)
            ]
        }

    @classmethod
    def build(cls, *args, **kwargs):
        kwargs.update(additional_content={'distractors': cls._make_distractors()})
        return super().build(*args, **kwargs)

    @classmethod
    def create(cls, *args, **kwargs):
        kwargs.update(additional_content={'distractors': cls._make_distractors()})
        return super().create(*args, **kwargs)


class TermImageMChoiceTextFactory(_ExerciseBase):
    type = ExerciseType.TERM_IMAGE_MCHOICE_TEXT
    term = factory.SubFactory(TermFactory)
    term_image = factory.SubFactory(
        TermImageFactory,
        term=factory.SelfAttribute('..term'),
    )

    @staticmethod
    def _make_distractors():
        distractors = TermFactory.create_batch(size=6)
        return {'term': [distractor.id for distractor in distractors]}

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
        distractors = TermFactory.create_batch(size=12)
        return {'term': [distractor.id for distractor in distractors]}

    @staticmethod
    def _make_connections():
        connections = TermFactory.create_batch(size=12)
        return {'term': [connection.id for connection in connections]}

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
