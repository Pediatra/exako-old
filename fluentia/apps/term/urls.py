from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.term_deck_home_view, name='term_deck'),
]