from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_report, name='submit_report'),
    path('list/', views.injury_list, name='injury_list'),
    path('players/', views.players_ajax, name='players_ajax'),
]
