from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import functions
from django.db.models.base import pre_save
from django.dispatch import receiver

from exako.apps.core.models import CustomManager
from exako.apps.term import constants
from exako.apps.term.validators import validate_term


class TermBase(models.Model):
    additional_content = models.JSONField(blank=True, null=True)
    objects = CustomManager()

    class Meta:
        abstract = True


class TermManager(models.Manager):
    def get(
        self,
        expression,
        language,
    ):
        term_query = (
            super()
            .get_queryset()
            .filter(
                expression__ct=expression,
                language=language,
            )
            .union(
                Term.objects.filter(
                    id__in=models.Subquery(
                        TermLexical.objects.select_related('term')
                        .filter(
                            type=constants.TermLexicalType.INFLECTION,
                            value__ct=expression,
                            term__language=language,
                        )
                        .values('term_id')
                    ),
                )
            )
            .first()
        )
        return term_query

    def search(self, expression, language):
        return (
            super()
            .get_queryset()
            .filter(
                models.Q(
                    expression__ct_icontains=expression,
                    language=language,
                )
                | models.Q(
                    id__in=models.Subquery(
                        TermLexical.objects.filter(
                            type=constants.TermLexicalType.INFLECTION,
                            value__ct_icontains=expression,
                            term__language=models.OuterRef('language'),
                        ).values_list('term_id', flat=True)
                    ),
                ),
            )
            .distinct()
        )

    def search_reverse(self, expression, language, translation_language):
        return (
            super()
            .get_queryset()
            .filter(
                id__in=models.Subquery(
                    TermDefinitionTranslation.objects.filter(
                        term_definition__term__language=language,
                        meaning__ct_icontains=expression,
                        language=translation_language,
                    ).values('term_definition__term_id')
                )
            )
        )


class Term(TermBase):
    expression = models.CharField(max_length=256)
    language = models.CharField(
        max_length=50,
        choices=constants.Language.choices,
    )

    objects = TermManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                functions.Lower('expression'),
                functions.Lower('language'),
                name='unique_term_expression',
            )
        ]
        indexes = [
            models.Index(
                functions.Lower('expression'),
                functions.Lower('language'),
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


class TermImage(TermBase):
    term = models.OneToOneField(Term, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='term')


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

    def get_part_of_speech(self):
        return constants.PartOfSpeech(int(self.part_of_speech)).label


class TermDefinitionTranslation(TermBase):
    language = models.CharField(
        max_length=50,
        choices=constants.Language.choices,
    )
    translation = models.CharField(max_length=255)
    meaning = models.TextField()
    term_definition = models.ForeignKey(TermDefinition, on_delete=models.CASCADE)

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


@receiver(pre_save)
def register_validators(sender, instance, **kwargs):
    validate_term(sender.__name__, instance=instance)


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
