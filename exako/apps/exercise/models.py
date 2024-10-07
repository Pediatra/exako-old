from django.db import models
from django.db.models.base import pre_save
from django.dispatch import receiver

from exako.apps.card.models import Card
from exako.apps.core.models import CustomManager
from exako.apps.exercise.constants import ExerciseType
from exako.apps.exercise.validators import validate_exercise
from exako.apps.term.constants import Language, Level
from exako.apps.term.models import (
    Term,
    TermDefinition,
    TermExample,
    TermImage,
    TermLexical,
    TermPronunciation,
)
from exako.apps.user.models import User


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

        if not isinstance(exercise_type, list):
            exercise_type = [exercise_type]
        if ExerciseType.RANDOM not in exercise_type:
            queryset = queryset.filter(type__in=exercise_type)

        if level:
            queryset = queryset.filter(level__in=level)

        if cardset_id:
            exercise_query = Exercise.objects.filter(
                term__in=Card.objects.filter(
                    cardset__user=user, cardset_id__in=cardset_id
                ).values('term')
            ).annotate(md5_seed=models.Value('0'))
            queryset = queryset.exclude(
                id__in=exercise_query.values_list('id', flat=True)
            )
            queryset = queryset.union(exercise_query)

        return queryset.values('type', 'id').order_by('md5_seed')


class Exercise(models.Model):
    language = models.CharField(
        max_length=50,
        choices=Language.choices,
    )
    type = models.CharField(max_length=50, choices=ExerciseType.choices)
    level = models.CharField(
        max_length=50,
        choices=Level.choices,
        null=True,
        blank=True,
    )
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


class ExerciseHistory(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    correct = models.BooleanField()
    response = models.JSONField(blank=True, null=True)
    request = models.JSONField(blank=True, null=True)

    @classmethod
    def get_current_streak(cls, user):
        histories = ExerciseHistory.objects.filter(user=user)
        first_invalid_subquery = models.Subquery(
            histories.filter(correct=False).order_by('-created_at').values('id')[:1]
        )
        return histories.filter(id__gt=first_invalid_subquery).count()


class RandomSeed(models.Func):
    function = 'MD5'
    template = '%(function)s(CAST(%(expressions)s AS VARCHAR) || %(seed)s)'


@receiver(pre_save, sender=Exercise)
def register_validators(sender, instance, **kwargs):
    validate_exercise(instance.type, exercise=instance)
