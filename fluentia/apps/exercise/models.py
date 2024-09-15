from django.db import models
from django.db.models.base import post_save, pre_save
from django.dispatch import receiver

from fluentia.apps.card.models import Card
from fluentia.apps.core.models import CustomManager
from fluentia.apps.exercise.constants import ExerciseType
from fluentia.apps.exercise.validators import validate_exercise
from fluentia.apps.term.constants import Language, Level
from fluentia.apps.term.models import (
    Term,
    TermDefinition,
    TermExample,
    TermImage,
    TermLexical,
    TermPronunciation,
)
from fluentia.apps.user.models import User


class ExerciseManager(CustomManager):
    def list(self, language, exercise_type, level, cardset_id, seed, user):
        queryset = (
            super()
            .get_queryset()
            .filter(language__in=language)
            .annotate(
                md5_seed=RandomSeed(
                    models.F('id'),
                    seed=seed,
                    output_field=models.CharField(),
                )
            )
        )

        if (
            exercise_type
            and isinstance(exercise_type, list)
            and ExerciseType.RANDOM not in exercise_type
            or exercise_type != ExerciseType.RANDOM
        ):
            queryset = queryset.filter(type__in=exercise_type)

        if level:
            level_query = ExerciseLevel.objects.filter(level__in=level).values(
                'exercise_id'
            )
            queryset = queryset.filter(id__in=level_query)

        if cardset_id:
            cardset_query = Card.objects.filter(
                cardset__user=user, cardset_id__in=cardset_id
            ).values('term')
            cardset_queryset = Exercise.objects.filter(
                models.Q(term__in=cardset_query),
            ).annotate(md5_seed=models.Value('0'))
            queryset = queryset.exclude(
                id__in=cardset_queryset.values_list('id', flat=True)
            )
            queryset = queryset.union(cardset_queryset)

        return queryset.values('type', 'id').order_by('md5_seed')


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
    term_image = models.ForeignKey(
        TermImage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    additional_content = models.JSONField(blank=True, null=True)
    objects = ExerciseManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['type', 'language', 'term_example'],
                name='unique_order_sentence',
                condition=models.Q(type=ExerciseType.ORDER_SENTENCE),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term', 'term_pronunciation'],
                name='unique_listen_term',
                condition=models.Q(type=ExerciseType.LISTEN_TERM),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term_lexical', 'term_pronunciation'],
                name='unique_listen_term_lexical',
                condition=models.Q(type=ExerciseType.LISTEN_TERM),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term', 'term_pronunciation'],
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
                fields=['type', 'language', 'term_lexical'],
                name='unique_speak_term_lexical',
                condition=models.Q(type=ExerciseType.SPEAK_TERM),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term_example'],
                name='unique_speak_sentence',
                condition=models.Q(type=ExerciseType.SPEAK_SENTENCE),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term', 'term_example'],
                name='unique_term_mchoice',
                condition=models.Q(type=ExerciseType.TERM_MCHOICE),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term_example', 'term_lexical'],
                name='unique_term_lexical_mchoice',
                condition=models.Q(type=ExerciseType.TERM_MCHOICE),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term_definition', 'term'],
                name='unique_term_definition_mchoice',
                condition=models.Q(type=ExerciseType.TERM_DEFINITION_MCHOICE),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term', 'term_image', 'term_pronunciation'],
                name='unique_term_image_mchoice',
                condition=models.Q(type=ExerciseType.TERM_IMAGE_MCHOICE),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term', 'term_image'],
                name='unique_term_image_mchoice_text',
                condition=models.Q(type=ExerciseType.TERM_IMAGE_MCHOICE_TEXT),
            ),
            models.UniqueConstraint(
                fields=['type', 'language', 'term'],
                name='unique_term_conection',
                condition=models.Q(type=ExerciseType.TERM_CONNECTION),
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


@receiver(pre_save, sender=Exercise)
def register_validators(sender, instance, **kwargs):
    validate_exercise(instance.type, exercise=instance)


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
