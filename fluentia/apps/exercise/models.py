from django.db import models
from django.db.models.base import post_save, pre_save
from ninja.errors import HttpError

from fluentia.apps.core.models import CustomManager
from fluentia.apps.exercise.constants import ExerciseType
from fluentia.apps.term.constants import Language, Level, TermLexicalType
from fluentia.apps.term.models import (
    Term,
    TermDefinition,
    TermExample,
    TermLexical,
    TermPronunciation,
)
from fluentia.apps.user.models import User


class Exercise(models.Model):
    language = models.CharField(
        max_length=50,
        choices=Language.choices,
    )
    type = models.CharField(max_length=50, choices=ExerciseType.choices)
    term = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    term_example = models.ForeignKey(
        TermExample,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    term_pronunciation = models.ForeignKey(
        TermPronunciation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    term_lexical = models.ForeignKey(
        TermLexical,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    term_definition = models.ForeignKey(
        TermDefinition,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    additional_content = models.JSONField(blank=True, null=True)
    objects = CustomManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['type', 'language', 'term_example'],
                name='unique_order_sentence',
                condition=models.Q(type=ExerciseType.ORDER_SENTENCE),
            ),
            models.UniqueConstraint(
                fields=[
                    'type',
                    'language',
                    'term',
                    'term_pronunciation',
                ],
                name='unique_listen_term',
                condition=models.Q(type=ExerciseType.LISTEN_TERM),
            ),
            models.UniqueConstraint(
                fields=[
                    'type',
                    'language',
                    'term',
                    'term_lexical',
                    'term_pronunciation',
                ],
                name='unique_listen_term_lexical',
                condition=models.Q(type=ExerciseType.LISTEN_TERM),
            ),
            models.UniqueConstraint(
                fields=[
                    'type',
                    'language',
                    'term',
                    'term_pronunciation',
                ],
                name='unique_listen_term_mchoice',
                condition=models.Q(type=ExerciseType.LISTEN_TERM_MCHOICE),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term_example', 'term_pronunciation'],
                name='unique_listen_sentence',
                condition=models.Q(type=ExerciseType.LISTEN_SENTENCE),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term'],
                name='unique_speak_term',
                condition=models.Q(type=ExerciseType.SPEAK_TERM),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term', 'term_lexical'],
                name='unique_speak_term_lexical',
                condition=models.Q(type=ExerciseType.SPEAK_TERM),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term_example'],
                name='unique_speak_sentence',
                condition=models.Q(type=ExerciseType.SPEAK_SENTENCE),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term'],
                name='unique_mchoice_term',
                condition=models.Q(type=ExerciseType.TERM_MCHOICE),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term', 'term_lexical'],
                name='unique_mchoice_term_lexical',
                condition=models.Q(type=ExerciseType.TERM_MCHOICE),
            ),
            models.UniqueConstraint(
                fields=[
                    'type',
                    'language',
                    'term_definition',
                    'term',
                ],
                name='unique_mchoice_term_definition',
                condition=models.Q(type=ExerciseType.TERM_DEFINITION_MCHOICE),
            ),
        ]


class ExerciseLevel(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    level = models.CharField(max_length=50, choices=Level.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint('exercise', 'level', name='unique_exercise_level')
        ]


class ExerciseHistory(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    correct = models.BooleanField()
    response = models.JSONField(blank=True, null=True)
    request = models.JSONField(blank=True, null=True)


class RandomSeed(models.Func):
    function = 'MD5'
    template = '%(function)s(CAST(%(expressions)s AS VARCHAR) || %(seed)s)'


def validate_listen_exercise(sender, instance, **kwargs):
    if instance.type not in [
        ExerciseType.LISTEN_SENTENCE,
        ExerciseType.LISTEN_TERM,
        ExerciseType.LISTEN_TERM_MCHOICE,
    ]:
        return

    if instance.term_pronunciation.audio_file is None:
        raise HttpError(
            status_code=422,
            message='pronunciation audio is not defined.',
        )


def validate_term_lexical_type(sender, instance, **kwargs):
    if not instance.term_lexical:
        return

    if instance.term_lexical.type != TermLexicalType.FORM:
        raise HttpError(
            status_code=422,
            message='exercise lexical only accepts TermLexicalType.FORM.',
        )


def validate_listen_mchoice_exercise(sender, instance, **kwargs):
    if instance.type != ExerciseType.LISTEN_TERM_MCHOICE:
        return

    count = TermLexical.objects.filter(
        term_id=instance.term_id,
        term_value_ref_id__in=models.Subquery(
            TermPronunciation.objects.filter(
                term_id=models.OuterRef('term_value_ref_id'),
                audio_file__isnull=False,
            ).values('term_id')
        ),
        type=TermLexicalType.RHYME,
    ).count()

    if count < 3:
        raise HttpError(
            status_code=422,
            message='mchoice exercises need to have at least 3 TermLexicalType.RHYME objects to form the alternatives.',
        )


def validate_order_sentence_distractors(sender, instance, **kwargs):
    if instance.type != ExerciseType.ORDER_SENTENCE:
        return

    if (
        not instance.additional_content
        or 'distractors' not in instance.additional_content
    ):
        return

    term_ids = list(
        Term.objects.filter(
            id__in=instance.additional_content['distractors']
        ).values_list('id', flat=True)
    )
    instance.additional_content['distractors'] = term_ids


def validate_term_mchoice_distractors(sender, instance, **kwargs):
    if instance.type != ExerciseType.TERM_MCHOICE:
        return

    distractor_error = HttpError(
        status_code=422,
        message='exercise needs at least 3 additional_content[distractors] to form the alternatives.',
    )
    if (
        not instance.additional_content
        or 'distractors' not in instance.additional_content
        or not isinstance(instance.additional_content['distractors'], list)
    ):
        raise distractor_error

    term_ids = list(
        Term.objects.filter(
            id__in=instance.additional_content['distractors']
        ).values_list('id', flat=True)
    )
    if len(term_ids) < 3:
        raise distractor_error
    instance.additional_content['distractors'] = term_ids


def validate_term_definition_mchoice_distractors(sender, instance, **kwargs):
    if instance.type != ExerciseType.TERM_DEFINITION_MCHOICE:
        return

    distractor_error = HttpError(
        status_code=422,
        message='exercise needs at least 3 additional_content[distractors] to form the alternatives.',
    )
    if (
        not instance.additional_content
        or 'distractors' not in instance.additional_content
        or not isinstance(instance.additional_content['distractors'], list)
    ):
        raise distractor_error

    definition_ids = list(
        TermDefinition.objects.filter(
            id__in=instance.additional_content['distractors']
        ).values_list('id', flat=True)
    )
    if len(definition_ids) < 3:
        raise distractor_error
    instance.additional_content['distractors'] = definition_ids


pre_save.connect(validate_listen_exercise, Exercise)
pre_save.connect(validate_term_lexical_type, Exercise)
pre_save.connect(validate_listen_mchoice_exercise, Exercise)
pre_save.connect(validate_order_sentence_distractors, Exercise)
pre_save.connect(validate_term_mchoice_distractors, Exercise)
pre_save.connect(validate_term_definition_mchoice_distractors, Exercise)


def create_exercise_level_term_example(sender, instance, **kwargs):
    if instance.type not in [
        ExerciseType.ORDER_SENTENCE,
        ExerciseType.LISTEN_SENTENCE,
        ExerciseType.SPEAK_SENTENCE,
    ]:
        return

    if not instance.term_example.level:
        return

    ExerciseLevel.objects.get_or_create(
        exercise=instance,
        level=instance.term_example.level,
    )


def create_exercise_level_term(sender, instance, **kwargs):
    if instance.type not in [
        ExerciseType.LISTEN_TERM,
        ExerciseType.LISTEN_TERM_MCHOICE,
        ExerciseType.SPEAK_TERM,
        ExerciseType.TERM_MCHOICE,
    ]:
        return

    term = instance.term if instance.term else instance.term_lexical.term
    levels = TermDefinition.objects.filter(term__id=term.id).values_list(
        'level', flat=True
    )
    for level in levels:
        ExerciseLevel.objects.get_or_create(exercise=instance, level=level)


def create_exercise_level_term_definition(sender, instance, **kwargs):
    if instance.type != ExerciseType.TERM_DEFINITION_MCHOICE:
        return

    ExerciseLevel.objects.get_or_create(
        exercise=instance,
        level=instance.term_definition.level,
    )


post_save.connect(create_exercise_level_term_example, Exercise)
post_save.connect(create_exercise_level_term, Exercise)
post_save.connect(create_exercise_level_term_definition, Exercise)
