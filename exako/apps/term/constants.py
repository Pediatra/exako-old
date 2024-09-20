from django.db.models import IntegerChoices, TextChoices
from django.utils.translation import gettext as _


class Level(TextChoices):
    BEGINNER = 'A1', _('Beginner')
    ELEMENTARY = 'A2', _('Elementary')
    INTERMEDIATE = 'B1', _('Intermediate')
    UPPER_INTERMEDIATE = 'B2', _('Upper Intermediate')
    ADVANCED = 'C1', _('Advanced')
    MASTER = 'C2', _('Master')


class PartOfSpeech(IntegerChoices):
    ADJECTIVE = 0, _('Adjective')
    NOUN = 1, _('Noun')
    VERB = 2, _('Verb')
    ADVERB = 3, _('Adverb')
    CONJUNCTION = 4, _('Conjunction')
    PREPOSITION = 5, _('Preposition')
    PRONOUN = 6, _('Pronoun')
    DETERMINER = 7, _('Determiner')
    NUMBER = 8, _('Number')
    PREDETERMINER = 9, _('Predeterminer')
    PREFIX = 10, _('Prefix')
    SUFFIX = 11, _('Suffix')
    SLANG = 12, _('Slang')
    PHRASAL_VERB = 13, _('Phrasal verb')
    LEXICAL = 14, _('Lexical')


class Language(TextChoices):
    PORTUGUESE = 'pt', _('Portuguese')
    ENGLISH = 'en', _('English')
    DEUTSCH = 'de', _('Deutsch')
    FRENCH = 'fr', _('French')
    SPANISH = 'es', _('Spanish')
    ITALIAN = 'it', _('Italian')
    CHINESE = 'zh', _('Chinese')
    JAPANESE = 'ja', _('Japanese')
    RUSSIAN = 'ru', _('Russian')


class TermLexicalType(IntegerChoices):
    SYNONYM = 0, _('Synonym')
    ANTONYM = 1, _('Antonym')
    INFLECTION = 2, _('Inflection')
    IDIOM = 3, _('Idiom')
    RHYME = 4, _('Rhyme')
