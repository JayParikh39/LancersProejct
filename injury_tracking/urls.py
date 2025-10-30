from django.urls import path
from . import views

app_name = 'injury_tracking'

urlpatterns = [
    # Dashboard views
    path('', views.dashboard, name='dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('coach/', views.coach_dashboard, name='coach_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('player/', views.player_dashboard, name='player_dashboard'),
    
    # Injury management
    path('injuries/', views.InjuryListView.as_view(), name='injury_list'),
    path('injuries/<int:pk>/', views.InjuryDetailView.as_view(), name='injury_detail'),
    path('injuries/create/', views.InjuryCreateView.as_view(), name='injury_create'),
    path('injuries/<int:pk>/update/', views.InjuryUpdateView.as_view(), name='injury_update'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics'),
    
    # API endpoints
    path('api/player/<int:player_id>/injuries/', views.get_player_injuries, name='player_injuries_api'),
    path('api/injury/<int:injury_id>/status/', views.update_injury_status, name='update_injury_status'),
]
