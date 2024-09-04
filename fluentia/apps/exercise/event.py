from fluentia.apps.exercise.constants import ExerciseType
from fluentia.apps.term.constants import TermLexicalType


def insert_order_exercise(sender, instance, created, **kwargs):
    return dict(
        language=instance.term_example.language,
        term_example=instance.term_example,
        translation_language=instance.language,
        type=ExerciseType.ORDER_SENTENCE,
    )


def insert_listen_term_mchoice_exercise(sender, instance, created, **kwargs):
    if not instance.term:
        return

    return dict(
        term=instance.term,
        term_pronunciation=instance,
        language=instance.language,
        type=ExerciseType.LISTEN_TERM_MCHOICE,
    )


def insert_listen_exercise(sender, instance, created, **kwargs):
    exercise_attr = {}
    if instance.term:
        exercise_attr = {
            'term': instance.term,
            'type': ExerciseType.LISTEN_TERM,
        }
    elif instance.term_example:
        exercise_attr = {
            'term_example': instance.term_example,
            'type': ExerciseType.LISTEN_SENTENCE,
        }
    elif instance.term_lexical:
        exercise_attr = {
            'term_lexical': instance.term_lexical,
            'type': ExerciseType.LISTEN_TERM,
        }
    return dict(
        **exercise_attr,
        term_pronunciation=instance,
        language=instance.language,
    )


def insert_speak_term_exercise(sender, instance, created, **kwargs):
    return dict(
        term=instance,
        language=instance.origin_language,
        type=ExerciseType.SPEAK_TERM,
    )


def insert_speak_term_lexical_exercise(sender, instance, created, **kwargs):

    return dict(
        term_lexical=instance,
        language=instance.term.origin_language,
        type=ExerciseType.SPEAK_TERM,
    )


def insert_speak_sentence_exercise(sender, instance, created, **kwargs):
    return dict(
        term_example=instance,
        type=ExerciseType.SPEAK_SENTENCE,
        language=instance.language,
    )


def insert_mchoice_term_exercise(sender, instance, created, **kwargs):
    if instance.type != TermLexicalType.ANTONYM:
        return

    return dict(
        term=instance.term,
        type=ExerciseType.TERM_MCHOICE,
        language=instance.term.origin_language,
    )


def insert_mchoice_term_lexical_exercise(sender, instance, created, **kwargs):

    return dict(
        term_example=instance,
        term=instance,
        term_lexical=instance,
        type=ExerciseType.TERM_MCHOICE,
        language=instance.term.origin_language,
    )


def insert_mchoice_term_translation_exercise(sender, instance, created, **kwargs):
    return dict(
        translation_language=instance.language,
        language=instance.term_definition.term.origin_language,
        term_definition=instance.term_definition,
        type=ExerciseType.TERM_DEFINITION_MCHOICE,
    )


# post_save.connect(insert_order_exercise, TermExampleTranslation)
# post_save.connect(insert_listen_term_mchoice_exercise, TermPronunciation)
# post_save.connect(insert_listen_exercise, TermPronunciation)
# post_save.connect(insert_speak_term_exercise, Term)
# post_save.connect(insert_speak_term_lexical_exercise, TermLexical)
# post_save.connect(insert_speak_sentence_exercise, TermExample)
# post_save.connect(insert_mchoice_term_exercise, TermLexical)
# post_save.connect(insert_mchoice_term_lexical_exercise, TermExampleLink)
# post_save.connect(insert_mchoice_term_translation_exercise, TermDefinition)
