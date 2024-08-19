from django.db.models import TextChoices
from django.utils.translation import gettext as _


class ExerciseType(TextChoices):
    ORDER_SENTENCE = 'order-sentence', _('Order sentence')
    LISTEN_TERM = 'listen-term', _('Listen term')
    LISTEN_TERM_MCHOICE = 'listen-term-mchoice', _('Listen term mulitple choice')
    LISTEN_SENTENCE = 'listen-sentence', _('Listen sentence')
    SPEAK_TERM = 'speak-term', _('Speak term')
    SPEAK_SENTENCE = 'speak-sentence', _('Speak sentence')
    TERM_MCHOICE = 'mchoice-term', _('Mulitple choice term')
    TERM_DEFINITION_MCHOICE = (
        'mchoice-term-definition',
        _('Multiple choice term definition'),
    )
    RANDOM = 'random', _('Random')


ORDER_SENTENCE_HEADER = _('Reordene as palavras para formar a frase correta.')
LISTEN_TERM_HEADER = _('Ouça o termo e digite exatamente o que você ouviu.')
LISTEN_SENTENCE_HEADER = _('Ouça a frase e digite exatamente o que você ouviu.')
LISTEN_MCHOICE_HEADER = _(
    'Ouça o termo e selecione a opção correta entre as alternativas fornecidas'
)
SPEAK_TERM_HEADER = _("Clique no microfone e pronuncie o termo '{term}'.")
SPEAK_SENTENCE_HEADER = _("Clique no microfone e pronuncie a frase '{sentence}'.")
MCHOICE_TERM_HEADER = _(
    "Complete a frase '{sentence}' escolhendo a alternativa correta abaixo."
)
MCHOICE_TERM_DEFINITION_HEADER = _(
    "Escolha a definição correta do termo '{term}' apresentado entre as opções fornecidas."
)
