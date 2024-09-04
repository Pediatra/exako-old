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


# <div id="lexicalTabContent">
#                 <div class="hidden p-4 rounded-lg bg-gray-50" id="synonyms" role="tabpanel" aria-labelledby="synonyms-tab">
#                     <h3 class="font-semibold text-lg mb-2 text-indigo-700">Sinônimos</h3>
#                     <div class="flex flex-wrap gap-2">
#                         <span class="bg-lime-100 text-lime-800 text-sm font-medium p-1 rounded-lg cursor-pointer">stunning</span>
#                         <span class="bg-lime-100 text-lime-800 text-sm font-medium p-1 rounded-lg cursor-pointer">dash</span>
#                         <span class="bg-lime-100 text-lime-800 text-sm font-medium p-1 rounded-lg cursor-pointer">jog</span>
#                         <span class="bg-lime-100 text-lime-800 text-sm font-medium p-1 rounded-lg cursor-pointer">race</span>
#                     </div>
#                 </div>
#                 <div class="hidden p-4 rounded-lg bg-gray-50" id="antonyms" role="tabpanel" aria-labelledby="antonyms-tab">
#                     <h3 class="font-semibold text-lg mb-2 text-indigo-700">Antônimos</h3>
#                     <div class="flex flex-wrap gap-2">
#                         <span class="bg-red-100 text-red-800 text-sm font-medium p-1 rounded-lg cursor-pointer">stunning</span>
#                         <span class="bg-red-100 text-red-800 text-sm font-medium p-1 rounded-lg cursor-pointer">dash</span>
#                         <span class="bg-red-100 text-red-800 text-sm font-medium p-1 rounded-lg cursor-pointer">jog</span>
#                         <span class="bg-red-100 text-red-800 text-sm font-medium p-1 rounded-lg cursor-pointer">race</span>
#                     </div>
#                 </div>
#                 <div class="hidden p-4 rounded-lg bg-gray-50" id="inflection" role="tabpanel" aria-labelledby="inflection-tab">
#                     <h3 class="font-semibold text-lg mb-2 text-indigo-700">Inflexões</h3>
#                     <div class="flex flex-wrap gap-2">
#                         <span class="bg-sky-100 text-sky-800 text-sm font-medium p-1 rounded-lg cursor-pointer">stunning</span>
#                         <span class="bg-sky-100 text-sky-800 text-sm font-medium p-1 rounded-lg cursor-pointer">dash</span>
#                         <span class="bg-sky-100 text-sky-800 text-sm font-medium p-1 rounded-lg cursor-pointer">jog</span>
#                         <span class="bg-sky-100 text-sky-800 text-sm font-medium p-1 rounded-lg cursor-pointer">race</span>
#                     </div>
#                 </div>
#                 <div class="hidden p-4 rounded-lg bg-gray-50" id="idioms" role="tabpanel" aria-labelledby="idioms-tab">
#                     <h3 class="font-semibold text-lg mb-2 text-indigo-700">Expressões Idiomáticas</h3>
#                     <div class="flex flex-wrap gap-2">
#                         <span class="bg-amber-100 text-amber-800 text-sm font-medium p-1 rounded-lg cursor-pointer">run out of time</span>
#                         <span class="bg-amber-100 text-amber-800 text-sm font-medium p-1 rounded-lg cursor-pointer">run into trouble</span>
#                         <span class="bg-amber-100 text-amber-800 text-sm font-medium p-1 rounded-lg cursor-pointer">run into trouble</span>
#                         <span class="bg-amber-100 text-amber-800 text-sm font-medium p-1 rounded-lg cursor-pointer">run into trouble</span>
#                     </div>
#                 </div>
#                 <div class="hidden p-4 rounded-lg bg-gray-50" id="rhymes" role="tabpanel" aria-labelledby="rhymes-tab">
#                     <h3 class="font-semibold text-lg mb-2 text-indigo-700">Rimas</h3>
#                     <div class="flex flex-wrap gap-2">
#                         <span class="bg-indigo-100 text-indigo-800 text-sm font-medium p-1 rounded-lg cursor-pointer">stunning</span>
#                         <span class="bg-indigo-100 text-indigo-800 text-sm font-medium p-1 rounded-lg cursor-pointer">dash</span>
#                         <span class="bg-indigo-100 text-indigo-800 text-sm font-medium p-1 rounded-lg cursor-pointer">jog</span>
#                         <span class="bg-indigo-100 text-indigo-800 text-sm font-medium p-1 rounded-lg cursor-pointer">race</span>
#                     <div>
#                 </div>
#             </div>
