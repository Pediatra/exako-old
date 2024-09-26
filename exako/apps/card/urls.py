from django.urls import path

from . import views

app_name = 'card'

urlpatterns = [
    path('', views.cardset_home_view, name='cardset_home'),
    path('partial/list', views.list_cardset_partial, name='list_cardset'),
    path('partial/create', views.create_cardset_partial, name='create_cardset'),
    path('partial/update/<int:cardset_id>', views.update_cardset_partial, name='update_cardset'),
    path('partial/add/<int:cardset_id>', views.add_cardset_partial, name='add_cardset'),
    path('partial/add/search/<int:cardset_id>', views.add_cardset_search_partial, name='add_cardset_search'),
    path('partial/add/create/<int:cardset_id>', views.add_cardset_create_partial, name='add_cardset_create'),
    path('view/<int:cardset_id>/', views.cardset_view, name='cardset_view'),
    path('partial/card/view/<int:cardset_id>/', views.card_view_partial, name='card_view'),
    path('partial/card/update/<int:cardset_id>/<int:card_id>', views.card_update_partial, name='card_update'),
]
