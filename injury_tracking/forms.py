from django import forms
from django.contrib.auth import get_user_model
from .models import (
    InjuryRecord, InjuryType, BodyPart, InjurySeverity, 
    InjuryFollowUp, TeamRoster, Event
)

User = get_user_model()

class InjuryReportForm(forms.ModelForm):
    """Form for doctors to report injuries"""
    
    class Meta:
        model = InjuryRecord
        fields = [
            'player', 'injury_date', 'injury_type', 'body_part', 'severity',
            'description', 'symptoms', 'treatment', 'treatment_notes',
            'estimated_recovery_time', 'requires_surgery', 'surgery_date',
            'follow_up_required', 'follow_up_date', 'follow_up_notes',
            'is_confidential'
        ]
        widgets = {
            'injury_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'treatment_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'follow_up_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'surgery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'player': forms.Select(attrs={'class': 'form-control'}),
            'injury_type': forms.Select(attrs={'class': 'form-control'}),
            'body_part': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'treatment': forms.Select(attrs={'class': 'form-control'}),
            'estimated_recovery_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'requires_surgery': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'follow_up_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_confidential': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Get authorized teams if method exists
        authorized_teams = None
        authorized_teams_count = 0
        if user and hasattr(user, 'get_authorized_teams'):
            try:
                authorized_teams = user.get_authorized_teams()
                # Check if it's a queryset and get count
                if authorized_teams is not None:
                    try:
                        authorized_teams_count = authorized_teams.count()
                    except Exception:
                        # If count fails, try len
                        try:
                            authorized_teams_count = len(authorized_teams) if authorized_teams else 0
                        except Exception:
                            authorized_teams_count = 0
                else:
                    authorized_teams_count = 0
            except Exception as e:
                # If method fails, treat as no teams
                authorized_teams = None
                authorized_teams_count = 0
        
        # Handle player queryset based on user role and team permissions
        if user and user.role == 'ADMIN':
            # Admins can see all players
            player_queryset = User.objects.filter(role='PLAYER').order_by('last_name', 'first_name')
        elif user and user.role == 'DOCTOR':
            # Doctors: check authorized teams
            if authorized_teams_count > 1:
                # Multiple teams - add team selector and filter players dynamically
                self.fields['team'] = forms.ModelChoiceField(
                    queryset=authorized_teams,
                    required=True,
                    empty_label="Select a team",
                    widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_team_selector'})
                )
                # Ensure 'team' appears first
                field_order = ['team'] + [name for name in self.fields if name != 'team']
                self.order_fields(field_order)
                
                # If POSTed, use selected team; else default to user's primary team
                selected_team = None
                data = args[0] if args else None
                if data and 'team' in data:
                    try:
                        selected_team = authorized_teams.get(id=data.get('team'))
                    except Exception:
                        selected_team = None
                if selected_team is None and user.team:
                    # Check if user's team is in authorized teams
                    try:
                        if user.team in list(authorized_teams):
                            selected_team = user.team
                    except Exception:
                        pass
                
                if selected_team:
                    player_queryset = User.objects.filter(role='PLAYER', team=selected_team).order_by('last_name', 'first_name')
                else:
                    # Show players from all authorized teams
                    player_queryset = User.objects.filter(role='PLAYER', team__in=authorized_teams).order_by('last_name', 'first_name')
            elif authorized_teams_count == 1:
                # Single team - filter to that team
                team = authorized_teams.first()
                if team:
                    player_queryset = User.objects.filter(role='PLAYER', team=team).order_by('last_name', 'first_name')
                else:
                    # Fallback to all players if team is None
                    player_queryset = User.objects.filter(role='PLAYER').order_by('last_name', 'first_name')
            elif user.team:
                # Doctor has a team assigned - use their team
                player_queryset = User.objects.filter(role='PLAYER', team=user.team).order_by('last_name', 'first_name')
            else:
                # Doctor with no team and no authorized teams - show all players
                # (This allows doctors to report injuries for any player until team is assigned)
                player_queryset = User.objects.filter(role='PLAYER').order_by('last_name', 'first_name')
        elif user and user.role == 'COACH':
            # Coaches: filter to their team
            if user.team:
                player_queryset = User.objects.filter(role='PLAYER', team=user.team).order_by('last_name', 'first_name')
            else:
                # Coach with no team - show no players (they need a team assigned)
                player_queryset = User.objects.filter(role='PLAYER', team=None)
        else:
            # Default: show all players (fallback)
            player_queryset = User.objects.filter(role='PLAYER').order_by('last_name', 'first_name')
        
        # Set the player queryset
        self.fields['player'].queryset = player_queryset

class InjuryUpdateForm(forms.ModelForm):
    """Form for updating injury record"""
    
    class Meta:
        model = InjuryRecord
        fields = [
            'status', 'description', 'symptoms', 'treatment', 'treatment_notes',
            'estimated_recovery_time', 'actual_recovery_time', 'return_to_play_date',
            'medical_clearance', 'clearance_date', 'requires_surgery', 'surgery_date',
            'follow_up_required', 'follow_up_date', 'follow_up_notes', 'is_confidential'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'treatment': forms.Select(attrs={'class': 'form-control'}),
            'treatment_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'estimated_recovery_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'actual_recovery_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'return_to_play_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'clearance_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'surgery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'follow_up_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'medical_clearance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_surgery': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'follow_up_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_confidential': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make status required
        self.fields['status'].required = True
        # Add help text
        self.fields['status'].help_text = 'Update the current status of the injury'
        self.fields['medical_clearance'].help_text = 'Check when player has received medical clearance to return to play'
        self.fields['clearance_date'].help_text = 'Date medical clearance was granted'
        self.fields['actual_recovery_time'].help_text = 'Actual recovery time in days (calculated automatically if status is set to RECOVERED)'

class InjuryFollowUpForm(forms.ModelForm):
    """Form for injury follow-ups"""
    
    class Meta:
        model = InjuryFollowUp
        fields = ['follow_up_date', 'notes', 'status_update']
        widgets = {
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'status_update': forms.Select(attrs={'class': 'form-control'}),
        }

class PlayerProfileForm(forms.ModelForm):
    """Form for players to update their profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class TeamRosterForm(forms.ModelForm):
    """Form for managing team roster"""
    
    class Meta:
        model = TeamRoster
        fields = ['player', 'position', 'jersey_number', 'is_active']
        widgets = {
            'player': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'jersey_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        
        if team:
            self.fields['player'].queryset = User.objects.filter(role='PLAYER', team=team)

class InjurySearchForm(forms.Form):
    """Form for searching and filtering injuries"""
    player = forms.ModelChoiceField(
        queryset=User.objects.filter(role='PLAYER'),
        required=False,
        empty_label="All Players",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    injury_type = forms.ModelChoiceField(
        queryset=InjuryType.objects.all(),
        required=False,
        empty_label="All Injury Types",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    body_part = forms.ModelChoiceField(
        queryset=BodyPart.objects.all(),
        required=False,
        empty_label="All Body Parts",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    severity = forms.ModelChoiceField(
        queryset=InjurySeverity.objects.all(),
        required=False,
        empty_label="All Severities",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + InjuryRecord.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

class EventForm(forms.ModelForm):
    """Form for coaches/admins to create team events"""
    class Meta:
        model = Event
        fields = ['event_type', 'title', 'description', 'location', 'start_datetime', 'end_datetime']
        widgets = {
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Optional team selector when user has multiple authorized teams
        authorized_teams = None
        if self.request_user and hasattr(self.request_user, 'get_authorized_teams'):
            authorized_teams = self.request_user.get_authorized_teams()
        if authorized_teams is not None and authorized_teams.count() > 1:
            self.fields['team'] = forms.ModelChoiceField(
                queryset=authorized_teams,
                required=True,
                empty_label=None,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
            # Ensure 'team' appears first using Django's order_fields
            field_order = ['team'] + [name for name in self.fields if name != 'team']
            self.order_fields(field_order)

    def save(self, commit=True):
        event = super().save(commit=False)
        if self.request_user:
            event.created_by = self.request_user
            # Respect selected team if present; otherwise use primary
            selected_team = self.cleaned_data.get('team') if 'team' in self.cleaned_data else None
            if selected_team is not None:
                event.team = selected_team
            elif hasattr(self.request_user, 'team') and self.request_user.team:
                event.team = self.request_user.team
        if commit:
            event.save()
        return event
