from django.db.models import OuterRef, Subquery
from ninja.errors import HttpError

from exako.apps.core.decorators import validate
from exako.apps.exercise.constants import ExerciseSubType, ExerciseType
from exako.apps.term.constants import TermLexicalType
from exako.apps.term.models import (
    Term,
    TermDefinition,
    TermExampleLink,
    TermImage,
    TermLexical,
    TermPronunciation,
)


@validate
def validate_exercise(): ...


@validate_exercise.register(
    [
        ExerciseType.LISTEN_TERM,
        ExerciseType.SPEAK_TERM,
        ExerciseType.TERM_MCHOICE,
    ]
)
def validate_sub_type_exercise(exercise):
    sub_type = exercise.additional_content['sub_type']
    if sub_type == ExerciseSubType.TERM_LEXICAL_VALUE:
        if not exercise.term_lexical.value:
            raise HttpError(
                status_code=422,
                message='ExerciseSubType.TERM_LEXICAL_VALUE requires term_lexical.value',
            )
    elif sub_type == ExerciseSubType.TERM_LEXICAL_TERM_REF:
        if not exercise.term_lexical.term_value_ref:
            raise HttpError(
                status_code=422,
                message='ExerciseSubType.TERM_LEXICAL_TERM_REF requires term_lexical.term_value_ref',
            )
    elif sub_type == ExerciseSubType.TERM:
        if not exercise.term:
            raise HttpError(
                status_code=422,
                message='ExerciseSubType.TERM requires term',
            )


@validate_exercise.register(
    [
        ExerciseType.LISTEN_SENTENCE,
        ExerciseType.SPEAK_SENTENCE,
    ]
)
def validate_term_example_reference_term_pronunciation(exercise):
    if (
        not exercise.term_pronunciation.term_example_id
        or exercise.term_pronunciation.term_example_id != exercise.term_example_id
    ):
        raise HttpError(
            status_code=422,
            message='term_example_id reference in term_pronunciation_id does not match.',
        )


@validate_exercise.register(
    [
        ExerciseType.LISTEN_TERM_MCHOICE,
        ExerciseType.TERM_IMAGE_MCHOICE,
    ]
)
def validate_term_reference_term_pronunciation(exercise):
    if (
        not exercise.term_pronunciation.term_id
        or exercise.term_pronunciation.term_id != exercise.term_id
    ):
        raise HttpError(
            status_code=422,
            message='term_id reference in term_pronunciation_id does not match.',
        )


@validate_exercise.register(
    [
        ExerciseType.LISTEN_TERM,
        ExerciseType.SPEAK_TERM,
    ]
)
def validate_term_sub_type_reference_term_pronunciation(exercise):
    if exercise.additional_content['sub_type'] != ExerciseSubType.TERM:
        return

    if (
        not exercise.term_pronunciation.term_id
        or exercise.term_pronunciation.term_id != exercise.term_id
    ):
        raise HttpError(
            status_code=422,
            message='term_id reference in term_pronunciation_id does not match.',
        )


@validate_exercise.register(
    [
        ExerciseType.LISTEN_TERM,
        ExerciseType.SPEAK_TERM,
    ]
)
def validate_term_lexical_value_sub_type_reference_term_pronunciation(exercise):
    if exercise.additional_content['sub_type'] != ExerciseSubType.TERM_LEXICAL_VALUE:
        return

    if (
        not exercise.term_pronunciation.term_lexical_id
        or exercise.term_pronunciation.term_lexical_id != exercise.term_lexical_id
    ):
        raise HttpError(
            status_code=422,
            message='term_lexical_id reference in term_pronunciation_id does not match.',
        )


@validate_exercise.register(
    [
        ExerciseType.LISTEN_TERM,
        ExerciseType.SPEAK_TERM,
    ]
)
def validate_term_lexical_ref_sub_type_reference_term_pronunciation(exercise):
    if exercise.additional_content['sub_type'] != ExerciseSubType.TERM_LEXICAL_TERM_REF:
        return

    if (
        not exercise.term_pronunciation.term_id
        or exercise.term_pronunciation.term_id
        != exercise.term_lexical.term_value_ref_id
    ):
        raise HttpError(
            status_code=422,
            message='term_id reference in term_pronunciation_id does not match.',
        )


@validate_exercise.register(ExerciseType.TERM_DEFINITION_MCHOICE)
def validate_term_reference_term_defintion(exercise):
    if exercise.term_definition.term_id != exercise.term_id:
        raise HttpError(
            status_code=422,
            message='term_id reference in term_definition_id does not match.',
        )


@validate_exercise.register(
    [
        ExerciseType.TERM_IMAGE_MCHOICE,
        ExerciseType.TERM_IMAGE_MCHOICE_TEXT,
    ]
)
def validate_term_reference_term_image(exercise):
    if exercise.term_image.term_id != exercise.term_id:
        raise HttpError(
            status_code=422,
            message='term_id reference in term_image_id does not match.',
        )


@validate_exercise.register(
    [
        ExerciseType.LISTEN_SENTENCE,
        ExerciseType.LISTEN_TERM,
        ExerciseType.LISTEN_TERM_MCHOICE,
        ExerciseType.SPEAK_TERM,
        ExerciseType.TERM_IMAGE_MCHOICE,
    ]
)
def validate_pronunciation_audio_file(exercise):
    if exercise.term_pronunciation.audio_file is None:
        raise HttpError(
            status_code=422,
            message='pronunciation audio file is required.',
        )


@validate_exercise.register(ExerciseType.LISTEN_TERM_MCHOICE)
def validate_listen_mchoice_exercise(exercise):
    count = TermLexical.objects.filter(
        term_id=exercise.term_id,
        term_value_ref_id__in=Subquery(
            TermPronunciation.objects.filter(
                term_id=OuterRef('term_value_ref_id'),
                audio_file__isnull=False,
            ).values('term_id')
        ),
        type=TermLexicalType.RHYME,
    ).count()

    if count < 3:
        raise HttpError(
            status_code=422,
            message='mchoice exercises need to have at least 3 TermLexicalType.RHYME objects to form the alternatives.',
        )


@validate_exercise.register(ExerciseType.TERM_MCHOICE)
def validate_term_mchoice_exercise_example_highlight(exercise):
    sub_type = exercise.additional_content['sub_type']
    if sub_type == ExerciseSubType.TERM_LEXICAL_VALUE:
        query = TermExampleLink.objects.filter(
            term_example_id=exercise.term_example_id,
            term_lexical_id=exercise.term_lexical_id,
        )
    elif sub_type == ExerciseSubType.TERM_LEXICAL_TERM_REF:
        query = TermExampleLink.objects.filter(
            term_example_id=exercise.term_example_id,
            term_id=exercise.term_lexical.term_value_ref_id,
        )
    else:
        query = TermExampleLink.objects.filter(
            term_example_id=exercise.term_example_id,
            term_id=exercise.term_id,
        )

    if not query.exists():
        raise HttpError(
            status_code=422,
            message='term mchoice exercise need term_example with highlight link.',
        )


@validate_exercise.register(ExerciseType.ORDER_SENTENCE)
def validate_order_sentence_distractors(exercise):
    if (
        not exercise.additional_content
        or 'distractors' not in exercise.additional_content
        and 'term' not in exercise.additional_content['distractors']
    ):
        return

    term_ids = list(
        Term.objects.filter(
            id__in=exercise.additional_content['distractors']['term']
        ).values_list('id', flat=True)
    )
    exercise.additional_content['distractors']['term'] = term_ids


@validate_exercise.register(ExerciseType.TERM_MCHOICE)
def validate_term_mchoice_distractors(exercise):
    is_term_lexical = bool(exercise.term_lexical_id)
    Model = TermLexical if is_term_lexical else Term
    distractor_key = 'term_lexical' if is_term_lexical else 'term'

    term_ids = list(
        Model.objects.filter(
            id__in=exercise.additional_content['distractors'][distractor_key]
        ).values_list('id', flat=True)
    )

    if len(term_ids) < 3:
        raise HttpError(
            status_code=422,
            message='exercise needs at least 3 additional_content[distractors] to form the alternatives.',
        )

    exercise.additional_content['distractors'][distractor_key] = term_ids


@validate_exercise.register(ExerciseType.TERM_DEFINITION_MCHOICE)
def validate_term_definition_mchoice_distractors(exercise):
    definition_ids = list(
        TermDefinition.objects.filter(
            id__in=exercise.additional_content['distractors']['term_definition']
        ).values_list('id', flat=True)
    )
    if len(definition_ids) < 3:
        raise HttpError(
            status_code=422,
            message='exercise needs at least 3 additional_content[distractors] to form the alternatives.',
        )
    exercise.additional_content['distractors']['term_definition'] = definition_ids


@validate_exercise.register(
    [
        ExerciseType.TERM_IMAGE_MCHOICE,
        ExerciseType.TERM_IMAGE_MCHOICE_TEXT,
    ]
)
def validate_term_image_distractors(exercise):
    is_image_mchoice = exercise.type == ExerciseType.TERM_IMAGE_MCHOICE
    Model = TermImage if is_image_mchoice else Term
    distractor_key = 'term_image' if is_image_mchoice else 'term'

    term_ids = list(
        Model.objects.filter(
            id__in=exercise.additional_content['distractors'][distractor_key]
        ).values_list('id', flat=True)
    )

    if len(term_ids) < 3:
        raise HttpError(
            status_code=422,
            message='exercise needs at least 3 additional_content[distractors] to form the alternatives.',
        )

    exercise.additional_content['distractors'][distractor_key] = term_ids


@validate_exercise.register(ExerciseType.TERM_CONNECTION)
def validate_term_connection_distractors(exercise):
    distractors_term_ids = list(
        Term.objects.filter(
            id__in=exercise.additional_content['distractors']['term']
        ).values_list('id', flat=True)
    )

    if len(distractors_term_ids) < 8:
        raise HttpError(
            status_code=422,
            message='exercise needs at least 8 additional_content[distractors] to form the connections.',
        )

    connections_term_ids = list(
        Term.objects.filter(
            id__in=exercise.additional_content['connections']['term']
        ).values_list('id', flat=True)
    )

    if len(connections_term_ids) < 4:
        raise HttpError(
            status_code=422,
            message='exercise needs at least 4 additional_content[connections] to form the connections.',
        )

    exercise.additional_content['distractors']['term'] = distractors_term_ids
    exercise.additional_content['connections']['term'] = connections_term_ids
