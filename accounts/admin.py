from django.contrib import admin
from django.utils import timezone
from .models import TeamPermission, TeamPermissionRequest


@admin.register(TeamPermission)
class TeamPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'role_scope', 'created_at']
    list_filter = ['role_scope', 'team', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'team__name']
    ordering = ['-created_at']


@admin.register(TeamPermissionRequest)
class TeamPermissionRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'role_scope', 'status', 'created_at', 'reviewed_by', 'reviewed_at']
    list_filter = ['status', 'role_scope', 'team', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'team__name']
    ordering = ['-created_at']
    actions = ['approve_requests', 'deny_requests']

    def save_model(self, request, obj, form, change):
        # Detect status transition to APPROVED and grant permission
        old_status = None
        if change:
            try:
                old = TeamPermissionRequest.objects.get(pk=obj.pk)
                old_status = old.status
            except TeamPermissionRequest.DoesNotExist:
                old_status = None

        # Stamp reviewer/time if status changed from pending
        if obj.status in ['APPROVED', 'DENIED'] and (not change or old_status != obj.status):
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()

        super().save_model(request, obj, form, change)

        if obj.status == 'APPROVED' and old_status != 'APPROVED':
            TeamPermission.objects.get_or_create(
                user=obj.user,
                team=obj.team,
                role_scope=obj.role_scope,
            )

    def approve_requests(self, request, queryset):
        for req in queryset.filter(status='PENDING'):
            req.status = 'APPROVED'
            req.reviewed_by = request.user
            req.reviewed_at = timezone.now()
            req.save()
            TeamPermission.objects.get_or_create(
                user=req.user,
                team=req.team,
                role_scope=req.role_scope,
            )
        self.message_user(request, 'Selected requests approved and access granted.')
    approve_requests.short_description = 'Approve selected requests'

    def deny_requests(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(
            status='DENIED'
        )
        for req in queryset.filter(status='DENIED'):
            req.reviewed_by = request.user
            req.reviewed_at = timezone.now()
            req.save()
        self.message_user(request, f'{updated} request(s) denied.')
    deny_requests.short_description = 'Deny selected requests'
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
