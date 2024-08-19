from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import functions
from django.db.models.base import pre_save
from ninja.errors import HttpError

from fluentia.apps.core.models import CustomManager
from fluentia.apps.term import constants


class TermBase(models.Model):
    additional_content = models.JSONField(blank=True, null=True)

    class Meta:
        abstract = True


class TermManager(models.Manager):
    def get(
        self,
        expression,
        origin_language,
    ):
        term_query = (
            super()
            .get_queryset()
            .filter(
                models.Q(
                    expression__ct=expression,
                    origin_language=origin_language,
                )
                | models.Q(
                    expression__in=models.Subquery(
                        TermLexical.objects.select_related('term')
                        .filter(
                            value__ct=expression,
                            term__origin_language=models.OuterRef('origin_language'),
                            type=constants.TermLexicalType.FORM,
                        )
                        .values_list('term__expression', flat=True)
                    ),
                ),
            )
        )
        return term_query


class Term(TermBase):
    expression = models.CharField(max_length=256)
    origin_language = models.CharField(
        max_length=50,
        choices=constants.Language.choices,
    )

    objects = TermManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                functions.Lower('expression'),
                functions.Lower('origin_language'),
                name='unique_term_expression',
            )
        ]
        indexes = [
            models.Index(
                functions.Lower('expression'),
                functions.Lower('origin_language'),
                name='term_inex_db',
            )
        ]


class TermLexical(TermBase):
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    term_value_ref = models.ForeignKey(
        Term,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='value_ref',
    )
    value = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=50, choices=constants.TermLexicalType.choices)

    objects = CustomManager()


def validate_term_value_ref(sender, instance, **kwargs):
    if not instance.term_value_ref:
        return

    if instance.term_value_ref == instance.term:
        raise HttpError(
            status_code=422,
            message='term_value_ref cannot be the same as term lexical reference.',
        )


pre_save.connect(validate_term_value_ref, TermLexical)


class TermExample(TermBase):
    language = models.CharField(max_length=50, choices=constants.Language.choices)
    example = models.CharField(max_length=255)
    level = models.CharField(
        max_length=50,
        choices=constants.Level.choices,
        blank=True,
        null=True,
    )


class TermExampleTranslation(TermBase):
    language = models.CharField(max_length=50, choices=constants.Language.choices)
    translation = models.CharField(max_length=255)
    term_example = models.ForeignKey(TermExample, on_delete=models.CASCADE)

    objects = CustomManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                'language',
                'term_example',
                name='term_example_translation_unique',
            )
        ]


class TermDefinition(TermBase):
    part_of_speech = models.CharField(
        max_length=50,
        choices=constants.PartOfSpeech.choices,
    )
    definition = models.TextField()
    level = models.CharField(
        max_length=50,
        choices=constants.Level.choices,
        blank=True,
        null=True,
    )
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    term_lexical = models.ForeignKey(
        TermLexical,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    objects = CustomManager()


class TermDefinitionTranslation(TermBase):
    language = models.CharField(
        max_length=50,
        choices=constants.Language.choices,
    )
    translation = models.CharField(max_length=255)
    meaning = models.TextField()
    term_definition = models.ForeignKey(TermDefinition, on_delete=models.CASCADE)

    objects = CustomManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                'language',
                'term_definition',
                name='term_definition_translation_unique_translation',
            )
        ]


class TermPronunciation(TermBase):
    description = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=50, choices=constants.Language.choices)
    phonetic = models.CharField(max_length=255)
    text = models.CharField(max_length=255, blank=True, null=True)
    audio_file = models.URLField(blank=True, null=True)
    term = models.OneToOneField(
        Term,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    term_example = models.OneToOneField(
        TermExample,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    term_lexical = models.OneToOneField(
        TermLexical,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    objects = CustomManager()


def validate_pronunciation_lexical_form(sender, instance, **kwargs):
    if not instance.term_lexical:
        return

    if instance.term_lexical.type != constants.TermLexicalType.FORM:
        raise HttpError(
            status_code=422,
            message='pronunciation lexical only accepts TermLexicalType.FORM',
        )


pre_save.connect(validate_pronunciation_lexical_form, TermPronunciation)


class TermExampleLink(TermBase):
    highlight = ArrayField(
        ArrayField(models.IntegerField(), size=2),
        blank=False,
        null=False,
    )
    term_example = models.ForeignKey(
        TermExample,
        on_delete=models.CASCADE,
    )
    term = models.ForeignKey(
        Term,
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
    term_lexical = models.ForeignKey(
        TermLexical,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    objects = CustomManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                'term', 'term_example', name='unique_term_example_link'
            ),
            models.UniqueConstraint(
                'term_definition', 'term_example', name='unique_term_definition_link'
            ),
            models.UniqueConstraint(
                'term_lexical', 'term_example', name='unique_term_lexical_link'
            ),
        ]


class TermExampleTranslationLink(TermBase):
    translation_language = models.CharField(
        max_length=50,
        choices=constants.Language.choices,
    )
    highlight = ArrayField(
        ArrayField(models.IntegerField(), size=2),
        blank=False,
        null=False,
    )
    term_example = models.ForeignKey(
        TermExample,
        on_delete=models.CASCADE,
    )
    term = models.ForeignKey(
        Term,
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
    term_lexical = models.ForeignKey(
        TermLexical,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    objects = CustomManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                'term',
                'term_example',
                'translation_language',
                name='unique_term_example_translation_link',
            ),
            models.UniqueConstraint(
                'term_definition',
                'term_example',
                'translation_language',
                name='unique_term_definition_translation_link',
            ),
            models.UniqueConstraint(
                'term_lexical',
                'term_example',
                'translation_language',
                name='unique_term_lexical_translation_link',
            ),
        ]


@models.CharField.register_lookup
@models.TextField.register_lookup
class CleanText(models.Lookup):
    lookup_name = 'ct'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'clean_text(%s) = clean_text(%s)' % (lhs, rhs), params


@models.CharField.register_lookup
@models.TextField.register_lookup
class CleanTextIContains(models.Lookup):
    lookup_name = 'ct_icontains'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f"clean_text({lhs}) LIKE '%%' || clean_text({rhs}) || '%%'", params
