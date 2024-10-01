from django.urls import path

from . import views

app_name = 'exercise'

urlpatterns = [
    path('', views.exercise_home, name='home'),
    path('partial/options', views.exercise_options_partial, name='options'),
    path('partial/view/<int:exercise_id>/<int:exercise_type>', views.exercise_view_partial, name='view'),
    path('partial/info/', views.exercise_info_partial, name='info'),
    path('test/<int:exercise_id>', views.test_view, name='test'),
]
