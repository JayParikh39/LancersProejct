from django import forms
from django.contrib.auth import get_user_model
from .models import (
    InjuryRecord, InjuryType, BodyPart, InjurySeverity, 
    InjuryFollowUp, TeamRoster
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
        
        # Filter players based on user's team if they're a coach
        if user and user.is_coach() and user.team:
            self.fields['player'].queryset = User.objects.filter(
                role='PLAYER', team=user.team
            )
        elif user and user.role == 'ADMIN':
            self.fields['player'].queryset = User.objects.filter(role='PLAYER')
        else:
            self.fields['player'].queryset = User.objects.filter(role='PLAYER')

class InjuryUpdateForm(forms.ModelForm):
    """Form for updating injury status"""
    
    class Meta:
        model = InjuryRecord
        fields = [
            'status', 'actual_recovery_time', 'return_to_play_date',
            'medical_clearance', 'clearance_date', 'treatment_notes'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'actual_recovery_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'return_to_play_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'clearance_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'treatment_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'medical_clearance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

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
