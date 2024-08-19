from django.db.models import TextChoices
from django.utils.translation import gettext as _


class Level(TextChoices):
    BEGINNER = 'A1', _('Beginner')
    ELEMENTARY = 'A2', _('Elementary')
    INTERMEDIATE = 'B1', _('Intermediate')
    UPPER_INTERMEDIATE = 'B2', _('Upper Intermediate')
    ADVANCED = 'C1', _('Advanced')
    MASTER = 'C2', _('Master')


class PartOfSpeech(TextChoices):
    ADJECTIVE = 'adjective', _('Adjective')
    NOUN = 'noun', _('Noun')
    VERB = 'verb', _('Verb')
    ADVERB = 'adverb', _('Adverb')
    CONJUNCTION = 'conjunction', _('Conjunction')
    PREPOSITION = 'preposition', _('Preposition')
    PRONOUN = 'pronoun', _('Pronoun')
    DETERMINER = 'determiner', _('Determiner')
    NUMBER = 'number', _('Number')
    PREDETERMINER = 'predeterminer', _('Predeterminer')
    PREFIX = 'prefix', _('Prefix')
    SUFFIX = 'suffix', _('Suffix')
    SLANG = 'slang', _('Slang')
    LEXICAL = 'lexical', _('Lexical')


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


class TermLexicalType(TextChoices):
    SYNONYM = 'synonym', _('Synonym')
    ANTONYM = 'antonym', _('Antonym')
    FORM = 'form', _('Form')
    IDIOM = 'idiom', _('Idiom')
    RHYME = 'rhyme', _('Rhyme')
