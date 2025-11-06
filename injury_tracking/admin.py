from django.contrib import admin
from django.utils.html import format_html
from .models import (
    InjuryType, BodyPart, InjurySeverity, InjuryRecord, 
    InjuryFollowUp, TeamRoster, InjuryAnalytics, Event
)

@admin.register(InjuryType)
class InjuryTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    ordering = ['name']

@admin.register(BodyPart)
class BodyPartAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']

@admin.register(InjurySeverity)
class InjurySeverityAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_code', 'description']
    search_fields = ['name']
    ordering = ['name']

@admin.register(InjuryRecord)
class InjuryRecordAdmin(admin.ModelAdmin):
    list_display = [
        'player', 'injury_type', 'body_part', 'severity', 
        'status', 'injury_date', 'reported_date', 'medical_clearance'
    ]
    list_filter = [
        'status', 'severity', 'injury_type', 'body_part', 
        'requires_surgery', 'medical_clearance', 'is_confidential',
        'injury_date', 'reported_date'
    ]
    search_fields = [
        'player__first_name', 'player__last_name', 'player__username',
        'description', 'symptoms'
    ]
    readonly_fields = ['reported_date', 'created_at', 'updated_at']
    date_hierarchy = 'injury_date'
    ordering = ['-injury_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('player', 'reported_by', 'injury_date', 'reported_date')
        }),
        ('Injury Details', {
            'fields': ('injury_type', 'body_part', 'severity', 'status', 'description', 'symptoms')
        }),
        ('Treatment', {
            'fields': ('treatment', 'treatment_notes', 'requires_surgery', 'surgery_date')
        }),
        ('Recovery', {
            'fields': ('estimated_recovery_time', 'actual_recovery_time', 'return_to_play_date')
        }),
        ('Medical Clearance', {
            'fields': ('medical_clearance', 'clearance_date')
        }),
        ('Follow-up', {
            'fields': ('follow_up_required', 'follow_up_date', 'follow_up_notes')
        }),
        ('Metadata', {
            'fields': ('is_confidential', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'player', 'injury_type', 'body_part', 'severity', 'reported_by'
        )

@admin.register(InjuryFollowUp)
class InjuryFollowUpAdmin(admin.ModelAdmin):
    list_display = ['injury', 'follow_up_date', 'status_update', 'created_by', 'created_at']
    list_filter = ['status_update', 'follow_up_date', 'created_at']
    search_fields = ['injury__player__first_name', 'injury__player__last_name', 'notes']
    ordering = ['-follow_up_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'injury', 'injury__player', 'created_by'
        )

@admin.register(TeamRoster)
class TeamRosterAdmin(admin.ModelAdmin):
    list_display = ['player', 'team', 'position', 'jersey_number', 'is_active', 'joined_date']
    list_filter = ['team', 'is_active', 'joined_date']
    search_fields = ['player__first_name', 'player__last_name', 'position']
    ordering = ['team', 'jersey_number']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('player', 'team')

@admin.register(InjuryAnalytics)
class InjuryAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'team', 'season_year', 'total_injuries', 'active_injuries', 
        'recovered_injuries', 'average_recovery_time'
    ]
    list_filter = ['season_year', 'team']
    search_fields = ['team__name']
    ordering = ['-season_year', 'team']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('team')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'team', 'start_datetime', 'end_datetime', 'created_by']
    list_filter = ['event_type', 'team', 'start_datetime']
    search_fields = ['title', 'description', 'location']
    ordering = ['-start_datetime']