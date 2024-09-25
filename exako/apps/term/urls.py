from django.urls import path

from . import views

app_name = 'term'

urlpatterns = [
    path('', views.term_home, name='home'),
    path('language/<str:language>', views.language_view, name='language'),
    path('term/<str:language>', views.term_view, name='view'),
    path('partial/search', views.search_term_partial, name='search'),
    path('partial/search/reverse', views.search_reverse_partial, name='search_reverse'),
    path('partial/index', views.index_term_partial, name='index'),
    path('partial/term_examples/<str:language>', views.term_examples_partial, name='term_examples'),
    path('partial/term_lexicals/<int:term_id>', views.term_lexicals_partial, name='term_lexicals'),
]
