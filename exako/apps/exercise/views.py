from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

from exako.apps.exercise.constants import ExerciseType, exercises_emoji_map
from exako.apps.exercise.exercises import exercises_map
from exako.apps.exercise import exercises
from exako.apps.exercise.models import Exercise, ExerciseHistory
from exako.apps.card.models import CardSet
from exako.apps.term.constants import Language, Level
from exako.apps.user.auth.decorator import login_required


def exercise_home(request):
    return render(
        request,
        'exercise/exercise_home.html',
        context={
            'exercises': {
                exercise.exercise_type: {
                    'title': exercise.title,
                    'emoji': exercises_emoji_map.get(exercise.exercise_type),
                    'short_description': exercise.short_description,
                    'count': Exercise.objects.filter(
                        type=exercise.exercise_type
                    ).count(),
                }
                for exercise in exercises_map
            }
        },
    )


@login_required
def exercise_options_partial(request):
    options = dict()
    options['language'] = {
        'alt_text': _('Selecione os idiomas'),
        'options': Language.choices,
    }
    options['exercise_type'] = {
        'alt_text': _('Selecione os exercícios'),
        'options': ExerciseType.choices,
    }
    options['level'] = {
        'alt_text': _('Selecione os níveis'),
        'options': [(level, level) for level, _ in Level.choices],
    }
    options['cardset'] = {
        'alt_text': _('Selecione os cardsets'),
        'options': [
            (cardset.id, cardset.name)
            for cardset in CardSet.objects.filter(user=request.user)
        ],
    }
    return render(
        request,
        'exercise/partials/exercise_options.html',
        context={'options': options},
    )


@login_required
def exercise_view_partial(request, exercise_type, exercise_id):
    exercise_class = next(
        (
            exercise
            for exercise in exercises_map
            if exercise.exercise_type == exercise_type
        ),
        None,
    )
    if exercise_class is None:
        return HttpResponse(status=400)
    exercise = exercise_class(exercise_id)
    print(exercise.correct_answer)
    return exercise.render_template(
        request,
        url=request.GET.get('url'),
        emoji=exercises_emoji_map.get(exercise.exercise_type),
    )


@login_required
def exercise_info_partial(request):
    return render(
        request,
        'exercise/partials/exercise_info.html',
        context={'current_streak': ExerciseHistory.get_current_streak(request.user)},
    )


def test_view(request, exercise_id):
    exercise = exercises.SpeakTermExercise(exercise_id)
    return exercise.render_template(request)
