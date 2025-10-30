from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

class InjuryType(models.Model):
    """Types of injuries that can occur"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class BodyPart(models.Model):
    """Body parts that can be injured"""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class InjurySeverity(models.Model):
    """Severity levels for injuries"""
    name = models.CharField(max_length=50, unique=True)
    color_code = models.CharField(max_length=7, help_text="Hex color code (e.g., #FF0000)")
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class InjuryRecord(models.Model):
    """Main injury record model"""
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('RECOVERING', 'Recovering'),
        ('RECOVERED', 'Recovered'),
        ('CHRONIC', 'Chronic'),
    ]
    
    TREATMENT_CHOICES = [
        ('REST', 'Rest'),
        ('PHYSIO', 'Physiotherapy'),
        ('SURGERY', 'Surgery'),
        ('MEDICATION', 'Medication'),
        ('OTHER', 'Other'),
    ]
    
    # Basic Information
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='injuries')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_injuries')
    injury_date = models.DateField()
    reported_date = models.DateTimeField(auto_now_add=True)
    
    # Injury Details
    injury_type = models.ForeignKey(InjuryType, on_delete=models.CASCADE)
    body_part = models.ForeignKey(BodyPart, on_delete=models.CASCADE)
    severity = models.ForeignKey(InjurySeverity, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Description and Notes
    description = models.TextField()
    symptoms = models.TextField(blank=True)
    treatment = models.CharField(max_length=20, choices=TREATMENT_CHOICES)
    treatment_notes = models.TextField(blank=True)
    
    # Recovery Information
    estimated_recovery_time = models.PositiveIntegerField(
        null=True, blank=True, 
        help_text="Estimated recovery time in days"
    )
    actual_recovery_time = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Actual recovery time in days"
    )
    return_to_play_date = models.DateField(null=True, blank=True)
    
    # Medical Information
    requires_surgery = models.BooleanField(default=False)
    surgery_date = models.DateField(null=True, blank=True)
    medical_clearance = models.BooleanField(default=False)
    clearance_date = models.DateField(null=True, blank=True)
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    
    # Metadata
    is_confidential = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-injury_date']
        permissions = [
            ("view_own_injuries", "Can view own injuries"),
            ("view_team_injuries", "Can view team injuries"),
            ("view_all_injuries", "Can view all injuries"),
        ]
    
    def __str__(self):
        return f"{self.player.get_full_name()} - {self.injury_type.name} ({self.injury_date})"
    
    @property
    def days_since_injury(self):
        """Calculate days since injury occurred"""
        return (timezone.now().date() - self.injury_date).days
    
    @property
    def is_fully_recovered(self):
        """Check if player is fully recovered"""
        return self.status == 'RECOVERED' and self.medical_clearance

class InjuryFollowUp(models.Model):
    """Follow-up records for injuries"""
    injury = models.ForeignKey(InjuryRecord, on_delete=models.CASCADE, related_name='follow_ups')
    follow_up_date = models.DateField()
    notes = models.TextField()
    status_update = models.CharField(max_length=20, choices=InjuryRecord.STATUS_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Follow-up for {self.injury} on {self.follow_up_date}"

class TeamRoster(models.Model):
    """Team roster management"""
    team = models.ForeignKey('accounts.Team', on_delete=models.CASCADE, related_name='roster')
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    position = models.CharField(max_length=50, blank=True)
    jersey_number = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['team', 'player']
    
    def __str__(self):
        return f"{self.player.get_full_name()} - {self.team.name}"

class InjuryAnalytics(models.Model):
    """Analytics data for injury tracking"""
    team = models.ForeignKey('accounts.Team', on_delete=models.CASCADE)
    season_year = models.PositiveIntegerField()
    total_injuries = models.PositiveIntegerField(default=0)
    active_injuries = models.PositiveIntegerField(default=0)
    recovered_injuries = models.PositiveIntegerField(default=0)
    most_common_injury_type = models.ForeignKey(InjuryType, on_delete=models.SET_NULL, null=True)
    most_common_body_part = models.ForeignKey(BodyPart, on_delete=models.SET_NULL, null=True)
    average_recovery_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['team', 'season_year']
    
    def __str__(self):
        return f"{self.team.name} - {self.season_year} Analytics"
