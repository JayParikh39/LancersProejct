from django.db import models
from django.conf import settings
from django.utils import timezone


class InjuryReport(models.Model):
    SEVERITY_CHOICES = [
        ('MINOR', 'Minor'),
        ('MODERATE', 'Moderate'),
        ('SEVERE', 'Severe'),
    ]
    BODY_PART_CHOICES = [
        ('HEAD', 'Head'),
        ('NECK', 'Neck'),
        ('SHOULDER', 'Shoulder'),
        ('ARM', 'Arm'),
        ('HAND', 'Hand'),
        ('CHEST', 'Chest'),
        ('BACK', 'Back'),
        ('HIP', 'Hip'),
        ('THIGH', 'Thigh'),
        ('KNEE', 'Knee'),
        ('LEG', 'Leg'),
        ('ANKLE', 'Ankle'),
        ('FOOT', 'Foot'),
        ('OTHER', 'Other'),
    ]

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='injury_reports',
        on_delete=models.CASCADE,
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='submitted_reports',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reported_date = models.DateField(auto_now_add=True)
    injury_date = models.DateField(null=True, blank=False)
    body_part = models.CharField(max_length=20, choices=BODY_PART_CHOICES, default='OTHER')
    diagnosis = models.CharField(max_length=255)
    mechanism = models.CharField(max_length=255, blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    imaging_required = models.BooleanField(default=False)
    IMAGING_CHOICES = [
        ('XRAY', 'X-ray'),
        ('MRI', 'MRI'),
        ('CT', 'CT'),
        ('US', 'Ultrasound'),
        ('NONE', 'None'),
    ]
    imaging_type = models.CharField(max_length=10, choices=IMAGING_CHOICES, default='NONE')
    imaging_details = models.CharField(max_length=255, blank=True)
    treatment_given = models.TextField(blank=True)
    recommended_followup = models.TextField(blank=True)
    time_lost_days = models.IntegerField(null=True, blank=True)
    expected_return_date = models.DateField(null=True, blank=True)
    restrictions = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-reported_date']

    def __str__(self):
        return f"{self.player} - {self.body_part} - {self.severity}"
