from django.db import models
from django.contrib.auth.models import AbstractUser

class Team(models.Model):
    GENDER_CHOICES = [
        ('M', 'Men'),
        ('W', 'Women'),
    ]
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('COACH', 'Coach'),
        ('DOCTOR', 'Doctor'),
        ('PLAYER', 'Player'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PLAYER')
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)
    is_registration_complete = models.BooleanField(default=False)
    
    # Personal Information
    phone = models.CharField(max_length=20, blank=True, help_text="Phone number")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True, help_text="Date of birth")
    address = models.TextField(blank=True, help_text="Home address")
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default="USA")
    
    # Emergency Contact Information
    emergency_contact_name = models.CharField(max_length=200, blank=True, help_text="Emergency contact full name")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, help_text="Emergency contact phone number")
    emergency_contact_relationship = models.CharField(max_length=100, blank=True, help_text="Relationship to emergency contact")
    emergency_contact_email = models.EmailField(blank=True, help_text="Emergency contact email")
    
    # Medical Information
    blood_type = models.CharField(max_length=10, blank=True, help_text="Blood type (A+, B-, O+, etc.)")
    medical_conditions = models.TextField(blank=True, help_text="Any known medical conditions")
    medications = models.TextField(blank=True, help_text="Current medications")
    allergies = models.TextField(blank=True, help_text="Known allergies")
    
    # Additional Information
    bio = models.TextField(blank=True, help_text="Personal bio or notes")
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def is_coach(self):
        return self.role == 'COACH'

    def is_doctor(self):
        return self.role == 'DOCTOR'

    def is_player(self):
        return self.role == 'PLAYER'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def get_full_address(self):
        address_parts = [self.address, self.city, self.state, self.zip_code]
        return ', '.join([part for part in address_parts if part.strip()])

class PlayerProfile(models.Model):
    # Personal Information
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    preferred_name = models.CharField(max_length=100, blank=True)
    alternate_email = models.EmailField(blank=True)
    student_id = models.CharField(max_length=20, blank=True)
    citizenship = models.CharField(max_length=100, blank=True)
    photo_id = models.ImageField(upload_to='player_ids/', blank=True, null=True)
    
    # Local Address (Current Residence)
    local_street_address = models.CharField(max_length=200, blank=True)
    local_city = models.CharField(max_length=100, blank=True)
    local_province = models.CharField(max_length=100, blank=True)
    local_postal_code = models.CharField(max_length=20, blank=True)
    
    # Permanent Address
    permanent_street_address = models.CharField(max_length=200, blank=True)
    permanent_city = models.CharField(max_length=100, blank=True)
    permanent_province_state = models.CharField(max_length=100, blank=True)
    permanent_postal_zip_code = models.CharField(max_length=20, blank=True)
    permanent_country = models.CharField(max_length=100, blank=True)
    
    # Sports & Team Information
    sport_gender_category = models.CharField(max_length=100, blank=True)
    height_feet = models.PositiveIntegerField(null=True, blank=True)
    height_inches = models.PositiveIntegerField(null=True, blank=True)
    weight_lbs = models.PositiveIntegerField(null=True, blank=True)
    hometown = models.CharField(max_length=100, blank=True)
    high_school = models.CharField(max_length=200, blank=True)
    high_school_coach_name = models.CharField(max_length=200, blank=True)
    position_event = models.CharField(max_length=100, blank=True)
    previous_club_team = models.CharField(max_length=200, blank=True)
    club_team_coach_name = models.CharField(max_length=200, blank=True)
    family_member_oua_usports = models.BooleanField(default=False)
    family_member_details = models.TextField(blank=True)
    
    # Academic Information
    school_type_last_year = models.CharField(max_length=100, blank=True)
    completed_18_credits_last_year = models.CharField(max_length=10, choices=[
        ('YES', 'Yes'),
        ('NO', 'No'),
        ('NA', 'N/A'),
    ], blank=True)
    academic_restrictions = models.CharField(max_length=10, choices=[
        ('YES', 'Yes'),
        ('NO', 'No'),
    ], blank=True)
    faculty = models.CharField(max_length=200, blank=True)
    program_of_study = models.CharField(max_length=200, blank=True)
    student_status = models.CharField(max_length=20, choices=[
        ('UNDERGRADUATE', 'Undergraduate'),
        ('GRADUATE', 'Graduate'),
        ('OTHER', 'Other'),
    ], blank=True)
    year_of_study = models.PositiveIntegerField(null=True, blank=True)
    registered_9_credits_per_term = models.CharField(max_length=10, choices=[
        ('YES', 'Yes'),
        ('NO', 'No'),
    ], blank=True)
    graduating_this_year = models.CharField(max_length=10, choices=[
        ('YES', 'Yes'),
        ('NO', 'No'),
    ], blank=True)
    
    # Legacy fields (keeping for backward compatibility)
    number = models.PositiveIntegerField(null=True, blank=True)
    position = models.CharField(max_length=50, blank=True)
    dob = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} Profile"
    
    def get_full_height(self):
        if self.height_feet and self.height_inches:
            return f"{self.height_feet}'{self.height_inches}\""
        return None
    
    def get_local_address(self):
        parts = [self.local_street_address, self.local_city, self.local_province, self.local_postal_code]
        return ', '.join([part for part in parts if part.strip()])
    
    def get_permanent_address(self):
        parts = [self.permanent_street_address, self.permanent_city, self.permanent_province_state, self.permanent_postal_zip_code, self.permanent_country]
        return ', '.join([part for part in parts if part.strip()])

class CoachProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    coaching_experience = models.PositiveIntegerField(null=True, blank=True, help_text="Years of coaching experience")
    specialization = models.CharField(max_length=100, blank=True, help_text="Coaching specialization")
    certification = models.CharField(max_length=100, blank=True, help_text="Coaching certifications")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} Coach Profile"

class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    medical_license = models.CharField(max_length=100, blank=True, help_text="Medical license number")
    specialization = models.CharField(max_length=100, blank=True, help_text="Medical specialization")
    years_experience = models.PositiveIntegerField(null=True, blank=True, help_text="Years of medical experience")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} Doctor Profile"

class EmailRoleMapping(models.Model):
    """Model to map email domains or specific emails to roles"""
    email_pattern = models.CharField(max_length=255, help_text="Email domain (e.g., @lancer.com) or specific email")
    role = models.CharField(max_length=10, choices=CustomUser.ROLE_CHOICES)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, help_text="Auto-assign team (optional)")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.email_pattern} -> {self.get_role_display()}"