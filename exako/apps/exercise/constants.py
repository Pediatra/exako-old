from django.db.models import IntegerChoices
from django.utils.translation import gettext as _


class ExerciseType(IntegerChoices):
    ORDER_SENTENCE = 0, _('Order sentence')
    LISTEN_TERM = 1, _('Listen term')
    LISTEN_TERM_MCHOICE = 2, _('Listen term mulitple choice')
    LISTEN_SENTENCE = 3, _('Listen sentence')
    SPEAK_TERM = 4, _('Speak term')
    SPEAK_SENTENCE = 5, _('Speak sentence')
    TERM_MCHOICE = 6, _('Mulitple choice term')
    TERM_DEFINITION_MCHOICE = (
        7,
        _('Multiple choice term definition'),
    )
    TERM_IMAGE_MCHOICE = 8, _('Term image multiple choice')
    TERM_IMAGE_MCHOICE_TEXT = (
        9,
        _('Term text image multiple choice'),
    )
    TERM_CONNECTION = 10, _('Term connection')
    RANDOM = 12, _('Random')


exercises_emoji_map = {
    ExerciseType.ORDER_SENTENCE: 'fa-sort-alpha-down',
    ExerciseType.LISTEN_TERM: 'fa-headphones',
    ExerciseType.LISTEN_TERM_MCHOICE: 'fa-headphones-alt',
    ExerciseType.LISTEN_SENTENCE: 'fa-volume-up',
    ExerciseType.SPEAK_TERM: 'fa-microphone',
    ExerciseType.SPEAK_SENTENCE: 'fa-microphone-alt',
    ExerciseType.TERM_MCHOICE: 'fa-list-ul',
    ExerciseType.TERM_DEFINITION_MCHOICE: 'fa-book',
    ExerciseType.TERM_IMAGE_MCHOICE: 'fa-image',
    ExerciseType.TERM_IMAGE_MCHOICE_TEXT: 'fa-image',
    ExerciseType.TERM_CONNECTION: 'fa-project-diagram',
}


class ExerciseSubType(IntegerChoices):
    TERM = 0, _('Term')
    TERM_LEXICAL_VALUE = 1, _('Term Lexical Value')
    TERM_LEXICAL_TERM_REF = 2, _('Term Lexical Term Reference')


ORDER_SENTENCE_HEADER = _('Reordene as palavras para formar a frase correta.')
LISTEN_TERM_HEADER = _('Ouça o termo e digite exatamente o que você ouviu.')
LISTEN_SENTENCE_HEADER = _('Ouça a frase e digite exatamente o que você ouviu.')
LISTEN_MCHOICE_HEADER = _(
    "Selecione a pronúncia correta do termo '{term}'."
)
SPEAK_TERM_HEADER = _("Clique no microfone e pronuncie o termo '{term}'.")
SPEAK_SENTENCE_HEADER = _("Clique no microfone e pronuncie a frase '{sentence}'.")
TERM_MCHOICE_HEADER = _(
    "Complete a frase '{sentence}' escolhendo a alternativa correta abaixo."
)
TERM_DEFINITION_MCHOICE_HEADER = _(
    "Escolha a definição correta do termo '{term}' apresentado entre as opções fornecidas."
)
TERM_IMAGE_MCHOICE_HEADER = _(
    'Escolha a imagem que corresponda com o termo você ouviu.'
)
TERM_IMAGE_MCHOICE_TEXT_HEADER = _('Escolha o termo que corresponda com a imagem.')
TERM_CONNECTION_HEADER = _(
    "Escolha 4 alternativas que tenham relação com o termo '{term}'."
)

CORRECT_FEEDBACK = _('Parabéns, você acertou!')
INCORRECT_FEEDBACK = _('Você errou!')
INCORRECT_FEEDBACK_CORRECT_ANSWER = _('Você errou, a resposta correta era: {answer}.')