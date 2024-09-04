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
    TERM_IMAGE_TEXT_MCHOICE = (
        9,
        _('Term text image multiple choice'),
    )
    TERM_CONNECTION = 10, _('Term connection')
    RANDOM = 12, _('Random')


ORDER_SENTENCE_HEADER = _('Reordene as palavras para formar a frase correta.')
LISTEN_TERM_HEADER = _('Ouça o termo e digite exatamente o que você ouviu.')
LISTEN_SENTENCE_HEADER = _('Ouça a frase e digite exatamente o que você ouviu.')
LISTEN_MCHOICE_HEADER = _(
    'Ouça o termo e selecione a opção correta entre as alternativas fornecidas'
)
SPEAK_TERM_HEADER = _("Clique no microfone e pronuncie o termo '{term}'.")
SPEAK_SENTENCE_HEADER = _("Clique no microfone e pronuncie a frase '{sentence}'.")
TERM_MCHOICE_HEADER = _(
    "Complete a frase '{sentence}' escolhendo a alternativa correta abaixo."
)
TERM_DEFINITION_MCHOICE_HEADER = _(
    "Escolha a definição correta do termo '{term}' apresentado entre as opções fornecidas."
)
TERM_IMAGE_MCHOICE_HEADER = _("Escolha a imagem que corresponda com o termo '{term}'.")
