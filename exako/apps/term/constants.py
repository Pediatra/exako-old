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
    PORTUGUESE_BRASILIAN = 'pt-BR', _('Portuguese Brazil')
    ENGLISH_USA = 'en-US', _('English USA')
    DEUTSCH = 'de', _('Deutsch')
    FRENCH = 'fr', _('French')
    SPANISH = 'es', _('Spanish')
    ITALIAN = 'it', _('Italian')
    CHINESE = 'zh', _('Chinese')
    JAPANESE = 'ja', _('Japanese')
    RUSSIAN = 'ru', _('Russian')


language_emoji_map = {
    Language.PORTUGUESE_BRASILIAN: '🇧🇷',
    Language.ENGLISH_USA: '🇺🇸',
    Language.DEUTSCH: '🇩🇪',
    Language.FRENCH: '🇫🇷',
    Language.SPANISH: '🇪🇸',
    Language.ITALIAN: '🇮🇹',
    Language.CHINESE: '🇨🇳',
    Language.JAPANESE: '🇯🇵',
    Language.RUSSIAN: '🇷🇺',
}

language_alphabet_map = {
    Language.PORTUGUESE_BRASILIAN: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    Language.ENGLISH_USA: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    Language.DEUTSCH: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜß',
    Language.FRENCH: 'ABCDEFGHIJKLMNOPQRSTUVWXYZÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸ',
    Language.SPANISH: 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ',
    Language.ITALIAN: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    Language.CHINESE: '阿贝色德饿佛日哈伊鸡卡勒马娜哦佩苦耳斯特乌维独埃克斯伊格黑克',
    Language.JAPANESE: 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん',
    Language.RUSSIAN: 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ',
}


class TermLexicalType(IntegerChoices):
    SYNONYM = 0, _('Synonym')
    ANTONYM = 1, _('Antonym')
    INFLECTION = 2, _('Inflection')
    IDIOM = 3, _('Idiom')
    RHYME = 4, _('Rhyme')
