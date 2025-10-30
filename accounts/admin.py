from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Team, PlayerProfile, CoachProfile, DoctorProfile, EmailRoleMapping

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'team', 'is_registration_complete')}),
        ('Personal Information', {'fields': ('phone', 'gender', 'date_of_birth', 'address', 'city', 'state', 'zip_code', 'country')}),
        ('Emergency Contact', {'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship', 'emergency_contact_email')}),
        ('Medical Information', {'fields': ('blood_type', 'medical_conditions', 'medications', 'allergies')}),
        ('Additional Information', {'fields': ('bio', 'profile_picture')}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'team', 'phone', 'is_registration_complete', 'is_active']
    list_filter = ['role', 'team', 'is_registration_complete', 'is_active', 'gender']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender']
    search_fields = ['name']

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Personal Information', {'fields': ('user', 'preferred_name', 'alternate_email', 'student_id', 'citizenship', 'photo_id')}),
        ('Local Address', {'fields': ('local_street_address', 'local_city', 'local_province', 'local_postal_code')}),
        ('Permanent Address', {'fields': ('permanent_street_address', 'permanent_city', 'permanent_province_state', 'permanent_postal_zip_code', 'permanent_country')}),
        ('Sports & Team Information', {'fields': ('sport_gender_category', 'height_feet', 'height_inches', 'weight_lbs', 'hometown', 'high_school', 'high_school_coach_name', 'position_event', 'previous_club_team', 'club_team_coach_name', 'family_member_oua_usports', 'family_member_details')}),
        ('Academic Information', {'fields': ('school_type_last_year', 'completed_18_credits_last_year', 'academic_restrictions', 'faculty', 'program_of_study', 'student_status', 'year_of_study', 'registered_9_credits_per_term', 'graduating_this_year')}),
        ('Legacy Fields', {'fields': ('number', 'position', 'dob')}),
    )
    list_display = ['user', 'student_id', 'sport_gender_category', 'position_event', 'year_of_study', 'hometown']
    list_filter = ['sport_gender_category', 'student_status', 'academic_restrictions', 'completed_18_credits_last_year']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'student_id', 'hometown', 'faculty']

@admin.register(CoachProfile)
class CoachProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'coaching_experience', 'specialization', 'certification']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'medical_license', 'specialization', 'years_experience']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

@admin.register(EmailRoleMapping)
class EmailRoleMappingAdmin(admin.ModelAdmin):
    list_display = ['email_pattern', 'role', 'team', 'is_active']
    list_filter = ['role', 'team', 'is_active']
    search_fields = ['email_pattern']
