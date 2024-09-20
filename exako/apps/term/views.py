from django.http import HttpResponse
from django.shortcuts import render

from exako.apps.user.auth.decorator import login_required


def term_deck_home_view(request):
    return render(request, 'abc.html')


@login_required
def home_home(request):
    return HttpResponse(
        'Text only, please.',
    )
