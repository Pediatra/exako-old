from django.shortcuts import render


def term_deck_home_view(request):
    return render(request, 'exercise/exercise_base.html')
